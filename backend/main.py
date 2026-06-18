from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
from pathlib import Path
import cv2
import numpy as np
import shutil
import uuid
import json
from json import JSONEncoder
from backend.core.constants import (
    DEFAULT_FRAME_SAMPLE_COUNT,
    DETECTION_MODES,
    FUSION_IOU_THRESHOLD,
    IMAGE_EXTENSIONS,
    MAX_VIDEO_BYTES,
    MAX_VIDEO_DURATION_MS,
    MAX_VIDEO_FRAMES,
    MAX_VIDEO_SAMPLING_ATTEMPTS,
    RESULT_DIR,
    SCENE_MODEL_PATH,
    SCENE_PERSON_CLASSES,
    SCENE_VEHICLE_CLASSES,
    TRACK_MAX_DISTANCE_RATIO,
    TREE_MIN_CONFIDENCE,
    UPLOAD_DIR,
    VIDEO_CONTEXT_RADIUS,
    VIDEO_CONTEXT_STRIDE_SECONDS,
    VIDEO_EXTENSIONS,
    VIDEO_PREFILTER_CANDIDATE_MULTIPLIER,
    VIDEO_QUALITY_THRESHOLD,
    VIDEO_VOTING_TOP_K,
    VISDRONE_MODEL_PATH,
    VISDRONE_PERSON_CLASSES,
    VISDRONE_VEHICLE_CLASSES,
)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.database import init_db
from backend.core.dependencies import get_current_user
from backend.routers.auth import router as auth_router
from backend.routers.logs import router as logs_router
from backend.routers.users import router as users_router
from backend.services.log_service import create_detection_log


class NumpyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


def convert_numpy_to_python(obj):
    """递归将 numpy 类型转换为 Python 原生类型"""
    if isinstance(obj, dict):
        return {k: convert_numpy_to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_to_python(item) for item in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj


app = FastAPI(title="无人机航拍图像智能识别后端")

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

# 加载 YOLO 模型
scene_model = YOLO(str(SCENE_MODEL_PATH))
visdrone_model = None
visdrone_model_error = ""
if VISDRONE_MODEL_PATH.exists():
    try:
        visdrone_model = YOLO(str(VISDRONE_MODEL_PATH))
    except Exception as exc:
        visdrone_model_error = str(exc)

# 让浏览器可以访问检测结果图片
app.mount("/results", StaticFiles(directory=str(RESULT_DIR)), name="results")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

init_db()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(logs_router)

def box_area(box):
    return max(0, box["x2"] - box["x1"]) * max(0, box["y2"] - box["y1"])


def box_iou(box_a, box_b):
    union = box_area(box_a) + box_area(box_b) - intersection_area(box_a, box_b)
    if union <= 0:
        return 0.0
    return intersection_area(box_a, box_b) / union


def intersection_area(box_a, box_b):
    x1 = max(box_a["x1"], box_b["x1"])
    y1 = max(box_a["y1"], box_b["y1"])
    x2 = min(box_a["x2"], box_b["x2"])
    y2 = min(box_a["y2"], box_b["y2"])
    return max(0, x2 - x1) * max(0, y2 - y1)


def center_of_box(box):
    return ((box["x1"] + box["x2"]) / 2, (box["y1"] + box["y2"]) / 2)


def bottom_center_of_box(box):
    return ((box["x1"] + box["x2"]) / 2, box["y2"])


def point_in_box(point, box):
    x, y = point
    return box["x1"] <= x <= box["x2"] and box["y1"] <= y <= box["y2"]


def expanded_box(box, margin_x, margin_y):
    return {
        "x1": box["x1"] - margin_x,
        "y1": box["y1"] - margin_y,
        "x2": box["x2"] + margin_x,
        "y2": box["y2"] + margin_y,
    }


def is_fine_vehicle(item):
    return item.get("model_role") == "fine_target" and item["class_name"] in VISDRONE_VEHICLE_CLASSES


def is_fine_person(item):
    return item.get("model_role") == "fine_target" and item["class_name"] in VISDRONE_PERSON_CLASSES


def simplify_polygon(points):
    if points is None or len(points) < 3:
        return []

    contour = np.asarray(points, dtype=np.float32)
    perimeter = cv2.arcLength(contour, True)
    epsilon = max(1.0, perimeter * 0.002)
    simplified = cv2.approxPolyDP(contour, epsilon, True).reshape(-1, 2)
    return [[round(float(x), 2), round(float(y), 2)] for x, y in simplified]


def polygon_area(polygon):
    if not polygon or len(polygon) < 3:
        return 0
    contour = np.asarray(polygon, dtype=np.float32)
    return float(abs(cv2.contourArea(contour)))


def point_in_polygon(point, polygon):
    if not polygon or len(polygon) < 3:
        return False

    contour = np.asarray(polygon, dtype=np.float32)
    return cv2.pointPolygonTest(contour, point, False) >= 0


def point_near_polygon(point, polygon, max_distance):
    if not polygon or len(polygon) < 3:
        return False

    contour = np.asarray(polygon, dtype=np.float32)
    distance = cv2.pointPolygonTest(contour, point, True)
    return distance >= -max_distance


def point_in_detection_mask(point, detection):
    mask = detection.get("mask") or {}
    polygon = mask.get("polygon") or []
    return point_in_polygon(point, polygon)


def point_near_detection_mask(point, detection, max_distance):
    mask = detection.get("mask") or {}
    polygon = mask.get("polygon") or []
    return point_near_polygon(point, polygon, max_distance)


def run_yolo_detection(yolo_model, image_path, model_role, conf=0.25):
    detections = []
    image_width = 0
    image_height = 0

    results = yolo_model.predict(
        source=str(image_path),
        conf=conf,
        stream=True,
        verbose=False,
    )

    for result in results:
        if result.orig_shape:
            image_height, image_width = result.orig_shape

        mask_polygons = []
        if result.masks is not None:
            mask_polygons = [simplify_polygon(points) for points in result.masks.xy]

        for index, box in enumerate(result.boxes):
            cls_id = int(box.cls[0])
            cls_name = yolo_model.names[cls_id]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            item = {
                "class_id": cls_id,
                "class_name": cls_name,
                "confidence": round(confidence, 4),
                "model_role": model_role,
                "box": {
                    "x1": round(x1, 2),
                    "y1": round(y1, 2),
                    "x2": round(x2, 2),
                    "y2": round(y2, 2)
                },
                "area": round((x2 - x1) * (y2 - y1), 2)
            }

            if index < len(mask_polygons) and mask_polygons[index]:
                item["mask"] = {
                    "polygon": mask_polygons[index],
                    "area": round(polygon_area(mask_polygons[index]), 2),
                }
                item["area"] = item["mask"]["area"]

            detections.append(item)

    return detections, image_width, image_height


def canonical_detection_group(item):
    class_name = item["class_name"]
    if class_name in VISDRONE_VEHICLE_CLASSES or class_name in SCENE_VEHICLE_CLASSES:
        return "vehicle"
    if class_name in VISDRONE_PERSON_CLASSES or class_name in SCENE_PERSON_CLASSES:
        return "person"
    return class_name


def preferred_model_role_for_group(group_name):
    if group_name in {"vehicle", "person"}:
        return "fine_target"
    return "scene"


def choose_preferred_detection(primary_item, candidate_item):
    primary_group = canonical_detection_group(primary_item)
    preferred_role = preferred_model_role_for_group(primary_group)

    if primary_item["model_role"] == candidate_item["model_role"]:
        return primary_item if primary_item["confidence"] >= candidate_item["confidence"] else candidate_item

    if primary_item["model_role"] == preferred_role:
        return primary_item
    if candidate_item["model_role"] == preferred_role:
        return candidate_item
    return primary_item if primary_item["confidence"] >= candidate_item["confidence"] else candidate_item


def merge_duplicate_candidates(detections):
    merged = []
    for item in detections:
        replaced = False
        item_group = canonical_detection_group(item)
        for index, kept_item in enumerate(merged):
            if canonical_detection_group(kept_item) != item_group:
                continue
            if box_iou(item["box"], kept_item["box"]) < FUSION_IOU_THRESHOLD:
                continue

            merged[index] = choose_preferred_detection(kept_item, item)
            replaced = True
            break

        if not replaced:
            merged.append(item)
    return merged


def fuse_model_detections(scene_detections, fine_detections):
    scene_semantic_detections = []
    scene_candidate_detections = []
    for item in scene_detections:
        if canonical_detection_group(item) in {"vehicle", "person"}:
            scene_candidate_detections.append(item)
        else:
            scene_semantic_detections.append(item)

    fused_target_detections = merge_duplicate_candidates(scene_candidate_detections + fine_detections)
    fused_scene_candidates = [item for item in fused_target_detections if item["model_role"] == "scene"]
    fused_fine_detections = [item for item in fused_target_detections if item["model_role"] == "fine_target"]
    fused_scene_detections = scene_semantic_detections + fused_scene_candidates

    return {
        "scene_detections": fused_scene_detections,
        "fine_detections": fused_fine_detections,
        "detections": fused_scene_detections + fused_fine_detections,
    }


def build_upload_url(file_name):
    return f"/uploads/{file_name}"


def build_result_url(file_name):
    return f"/results/{file_name}"


def detect_media_kind(file: UploadFile):
    suffix = Path(file.filename or "").suffix.lower()
    content_type = (file.content_type or "").lower()

    if content_type.startswith("video/") or suffix in VIDEO_EXTENSIONS:
        return "video"
    if content_type.startswith("image/") or suffix in IMAGE_EXTENSIONS:
        return "image"
    raise HTTPException(status_code=400, detail="仅支持图片或视频文件上传")


def save_upload_file(upload: UploadFile, target_path: Path):
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)


def compute_visual_quality(frame, previous_gray=None):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = float(np.mean(gray))
    edge_density = float(np.count_nonzero(cv2.Canny(gray, 80, 160))) / max(1, gray.size)
    motion_delta = 0.0
    if previous_gray is not None and previous_gray.shape == gray.shape:
        motion_delta = float(np.mean(cv2.absdiff(gray, previous_gray)))

    brightness_score = max(0.0, 1.0 - min(abs(brightness - 128.0) / 128.0, 1.0))
    return {
        "gray": gray,
        "sharpness": round(float(sharpness), 2),
        "brightness": round(brightness, 2),
        "brightness_score": round(brightness_score * 100, 2),
        "edge_density": round(edge_density * 100, 2),
        "motion_delta": round(motion_delta, 2),
        "prefilter_score": round(
            min(45.0, sharpness / 12.0)
            + brightness_score * 20.0
            + min(20.0, edge_density * 160.0)
            + min(15.0, motion_delta / 3.0),
            2,
        ),
    }


def score_frame_quality(detections, analysis, visual_quality=None):
    if not detections:
        return 0.0

    average_confidence = sum(item["confidence"] for item in detections) / len(detections)
    low_confidence_count = analysis["metrics"]["low_confidence_count"]
    scene_bonus = 8 if analysis["scene_type"] != "未识别到明确巡检场景" else 0
    module_bonus = sum(1 for module in analysis["modules"] if module["score"] >= 20) * 3
    key_class_bonus = 0
    if analysis["metrics"]["vehicle_count"] > 0:
        key_class_bonus += 6
    if "道路区域" in analysis["scene_tags"]:
        key_class_bonus += 6
    visual_bonus = min(18.0, (visual_quality or {}).get("prefilter_score", 0.0) * 0.18)
    quality_score = (
        min(30, len(detections) * 6)
        + average_confidence * 35
        + scene_bonus
        + module_bonus
        + key_class_bonus
        + visual_bonus
        - low_confidence_count * 4
    )
    return round(max(0.0, quality_score), 2)


def run_detection_pipeline(image_path, detection_mode):
    raw_scene_detections = []
    raw_fine_detections = []
    image_width = 0
    image_height = 0
    models_used = []

    if detection_mode in {"fusion", "scene"}:
        raw_scene_detections, image_width, image_height = run_yolo_detection(
            scene_model,
            image_path,
            "scene",
            conf=0.25,
        )
        models_used.append("scene")

    if detection_mode in {"fusion", "fine"} and visdrone_model:
        raw_fine_detections, fine_width, fine_height = run_yolo_detection(
            visdrone_model,
            image_path,
            "fine_target",
            conf=0.25,
        )
        image_width = image_width or fine_width
        image_height = image_height or fine_height
        models_used.append("visdrone")

    fused_detection_data = fuse_model_detections(raw_scene_detections, raw_fine_detections)
    scene_detections = fused_detection_data["scene_detections"]
    fine_detections = fused_detection_data["fine_detections"]
    detections = fused_detection_data["detections"]
    class_count = {}
    for item in detections:
        name = item["class_name"]
        class_count[name] = class_count.get(name, 0) + 1

    analysis = analyze_scene(scene_detections, class_count, image_width, image_height, fine_detections)
    quality_score = score_frame_quality(detections, analysis)

    return {
        "scene_detections": scene_detections,
        "fine_detections": fine_detections,
        "detections": detections,
        "class_count": class_count,
        "analysis": analysis,
        "image_width": image_width,
        "image_height": image_height,
        "models_used": models_used,
        "quality_score": quality_score,
        "fusion": {
            "raw_scene_count": len(raw_scene_detections),
            "raw_fine_count": len(raw_fine_detections),
            "fused_scene_count": len(scene_detections),
            "fused_fine_count": len(fine_detections),
            "removed_duplicates": len(raw_scene_detections) + len(raw_fine_detections) - len(detections),
        },
    }


def extract_video_frames(video_path, output_prefix, attempt_index, frame_count):
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise HTTPException(status_code=400, detail="视频文件无法读取，请确认格式是否正确")

    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
    if total_frames <= 0 or fps <= 0:
        capture.release()
        raise HTTPException(status_code=400, detail="视频中未读取到有效帧")

    if total_frames > MAX_VIDEO_FRAMES:
        capture.release()
        raise HTTPException(
            status_code=413,
            detail=f"视频帧数过多（{total_frames} 帧 > {MAX_VIDEO_FRAMES} 帧），请裁剪后再上传",
        )

    duration_ms = round((total_frames / fps) * 1000, 2)
    if duration_ms > MAX_VIDEO_DURATION_MS:
        capture.release()
        raise HTTPException(
            status_code=413,
            detail=f"视频时长过长（{round(duration_ms / 1000, 1)} 秒），请裁剪到 {MAX_VIDEO_DURATION_MS // 60000} 分钟以内",
        )

    usable_frames = max(total_frames - 1, 1)
    step = usable_frames / (frame_count + 1)
    # 每轮使用视频的不同时间段，确保帧不重叠
    # 第1轮：0-1/3，第2轮：1/3-2/3，第3轮：2/3-1
    time_slot_start = attempt_index / MAX_VIDEO_SAMPLING_ATTEMPTS
    time_slot_end = (attempt_index + 1) / MAX_VIDEO_SAMPLING_ATTEMPTS
    slot_frame_start = int(usable_frames * time_slot_start)
    slot_frame_end = int(usable_frames * time_slot_end)
    slot_usable = max(slot_frame_end - slot_frame_start, 1)
    frame_indices = []
    for position in range(frame_count):
        candidate_index = slot_frame_start + int(min(slot_usable - 1, round((position + 1) * slot_usable / (frame_count + 1))))
        if candidate_index not in frame_indices and slot_frame_start <= candidate_index < slot_frame_end:
            frame_indices.append(candidate_index)
    # 确保至少有 frame_count 个不同的帧
    while len(frame_indices) < frame_count:
        for idx in range(slot_frame_start, slot_frame_end):
            if idx not in frame_indices:
                frame_indices.append(idx)
                if len(frame_indices) >= frame_count:
                    break

    candidate_multiplier = max(2, VIDEO_PREFILTER_CANDIDATE_MULTIPLIER)
    candidate_indices = []
    candidate_count = max(frame_count, frame_count * candidate_multiplier)
    # 候选帧也在当前时间槽内选择
    candidate_step = slot_usable / (candidate_count + 1)
    for position in range(candidate_count):
        candidate_index = slot_frame_start + int(min(slot_usable - 1, round((position + 1) * candidate_step)))
        if candidate_index not in candidate_indices and slot_frame_start <= candidate_index < slot_frame_end:
            candidate_indices.append(candidate_index)

    candidate_frames = []
    previous_gray = None
    for target_index in candidate_indices:
        frame = _read_frame_at(capture, target_index, total_frames)
        if frame is None:
            continue
        visual_quality = compute_visual_quality(frame, previous_gray)
        previous_gray = visual_quality.pop("gray")
        candidate_frames.append(
            {
                "frame_index": target_index,
                "frame": frame,
                "visual_quality": visual_quality,
            }
        )

    if not candidate_frames:
        capture.release()
        raise HTTPException(status_code=400, detail="视频抽帧失败，未能读取到任何有效画面，请尝试重新转码后上传")

    candidate_frames.sort(
        key=lambda item: (item["visual_quality"]["prefilter_score"], item["visual_quality"]["sharpness"]),
        reverse=True,
    )
    selected_candidates = sorted(candidate_frames[:frame_count], key=lambda item: item["frame_index"])

    extracted_frames = []
    for local_index, candidate in enumerate(selected_candidates):
        frame_index = candidate["frame_index"]
        frame = candidate["frame"]
        frame_name = f"{output_prefix}_attempt{attempt_index + 1}_frame{local_index + 1}.jpg"
        frame_path = UPLOAD_DIR / frame_name
        cv2.imwrite(str(frame_path), frame)
        timestamp_ms = round((frame_index / fps) * 1000, 2) if fps > 0 else None
        extracted_frames.append(
            {
                "frame_index": frame_index,
                "timestamp_ms": timestamp_ms,
                "path": frame_path,
                "source_image_url": build_upload_url(frame_name),
                "visual_quality": candidate["visual_quality"],
            }
        )

    capture.release()
    return {
        "fps": round(fps, 3) if fps > 0 else 0,
        "total_frames": total_frames,
        "duration_ms": duration_ms,
        "frames": extracted_frames,
        "candidate_count": len(candidate_frames),
    }


def _cleanup_video_temp_frames(file_id: str, keep_frame_path: str | None = None):
    """清理抽帧过程中产生的临时帧文件，可选择性保留最终被使用的帧。"""
    pattern = f"{file_id}_attempt*.jpg"
    for stale in UPLOAD_DIR.glob(pattern):
        if keep_frame_path and stale.name == Path(keep_frame_path).name:
            continue
        try:
            stale.unlink()
        except OSError:
            continue
    context_pattern = f"{file_id}_context*.jpg"
    for stale in UPLOAD_DIR.glob(context_pattern):
        try:
            stale.unlink()
        except OSError:
            continue
    for stale in UPLOAD_DIR.glob(context_pattern):
        try:
            stale.unlink()
        except OSError:
            continue


def _read_frame_at(capture, target_index, total_frames):
    """优先按帧号 seek 读取，失败时回退到顺序读取以兼容部分 codec。"""
    target_index = max(0, min(target_index, max(total_frames - 1, 0)))
    capture.set(cv2.CAP_PROP_POS_FRAMES, target_index)
    ok, frame = capture.read()
    if ok and frame is not None:
        actual_index = int(capture.get(cv2.CAP_PROP_POS_FRAMES) or 0)
        if abs(actual_index - target_index) <= 2 or target_index == 0:
            return frame
    return _read_frame_sequential(capture, target_index, total_frames)


def _read_frame_sequential(capture, target_index, total_frames):
    """从头顺序读取到目标帧号，用于在 seek 不准确时补救。"""
    capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
    current = 0
    while current < target_index:
        ok, frame = capture.read()
        if not ok or frame is None:
            return None
        current += 1
    ok, frame = capture.read()
    if not ok or frame is None:
        return None
    return frame


def build_report(
    detection_mode,
    scene_detections,
    fine_detections,
    detections,
    class_count,
    analysis,
    fusion_summary=None,
    media_summary="",
    video_temporal_context=None,
):
    if detections:
        main_class = max(class_count, key=class_count.get)
        fine_target_count = len(fine_detections)
        fusion_text = ""
        if fusion_summary and fusion_summary["removed_duplicates"] > 0:
            fusion_text = f"融合去重后剔除了 {fusion_summary['removed_duplicates']} 个重复目标。"
        
        # 构建时序分析报告（如果存在）
        temporal_text = ""
        if video_temporal_context:
            module = video_temporal_context.get("module", {})
            details = module.get("details", {})
            score = module.get("score", 0)
            status = module.get("status", "正常")
            
            # 收集所有危险行为
            danger_items = []
            if details.get("vehicle_offroad", 0) > 0:
                danger_items.append(f"车辆越界{details['vehicle_offroad']}条")
            if details.get("vehicle_edge", 0) > 0:
                danger_items.append(f"车辆边缘行驶{details['vehicle_edge']}条")
            if details.get("vehicle_lane_change", 0) > 0:
                danger_items.append(f"车辆变道{details['vehicle_lane_change']}条")
            if details.get("person_offroad", 0) > 0:
                danger_items.append(f"行人道路外活动{details['person_offroad']}条")
            
            if danger_items:
                temporal_text = (
                    f"连续帧时序分析（锚点帧±2帧，共5帧）发现："
                    f"{'、'.join(danger_items)}。"
                    f"时序风险评分 {score}，状态：{status}。"
                    f"{module.get('reason', '')}"
                )
            else:
                temporal_text = (
                    f"连续帧时序分析（锚点帧±2帧，共5帧）未发现明显违规或危险行为，"
                    f"车辆行驶状态正常。{module.get('reason', '')}"
                )
        
        return (
            f"本次采用{DETECTION_MODES[detection_mode]}{media_summary}，共检测到 {len(detections)} 个目标。"
            f"其中场景要素 {len(scene_detections)} 个，细粒度目标 {fine_target_count} 个。"
            f"其中数量最多的类别为 {main_class}，共 {class_count[main_class]} 个。"
            f"{fusion_text}"
            f"{analysis['summary']}"
            + (f" {temporal_text}" if temporal_text else "")
        )

    return (
        f"本次采用{DETECTION_MODES[detection_mode]}{media_summary}，未检测到当前模型可识别的目标。"
        "可能原因是图像中目标不属于当前模型类别，或目标过小、置信度较低。"
    )


def aggregate_frame_detections(frame_candidates):
    if not frame_candidates:
        return None, None, []

    # 随机选择锚点帧，而不是总是选质量最高或风险最低的
    # 这样能更好地覆盖视频的不同状态
    import random
    random.seed()  # 使用时间作为随机种子
    best_candidate = random.choice(frame_candidates)
    top_candidates = frame_candidates[:VIDEO_VOTING_TOP_K]

    scene_type_votes = {}
    risk_level_votes = {}
    class_presence = {}
    quality_scores = []
    risk_scores = []
    total_count_sum = 0
    class_count_peak = {}
    all_frame_detections = []  # 收集所有帧的检测结果用于综合评分

    for candidate in frame_candidates:  # 使用所有帧而不是只使用 top_candidates
        detection = candidate["detection"]
        analysis = detection["analysis"]
        scene_type = analysis["scene_type"]
        risk_level = analysis["risk_level"]
        scene_type_votes[scene_type] = scene_type_votes.get(scene_type, 0) + 1
        risk_level_votes[risk_level] = risk_level_votes.get(risk_level, 0) + 1
        quality_scores.append(detection["quality_score"])
        risk_scores.append(analysis["risk_score"])
        total_count_sum += len(detection["detections"])

        # 收集每帧的检测类别统计
        frame_class_count = detection.get("class_count", {})
        for class_name, count in frame_class_count.items():
            class_presence[class_name] = class_presence.get(class_name, 0) + 1
            class_count_peak[class_name] = max(class_count_peak.get(class_name, 0), count)

        # 收集所有帧的检测详情
        all_frame_detections.append({
            "frame_index": candidate["frame"]["frame_index"],
            "timestamp_ms": candidate["frame"].get("timestamp_ms"),
            "total_count": len(detection["detections"]),
            "class_count": frame_class_count,
            "risk_level": risk_level,
            "risk_score": analysis["risk_score"],
            "quality_score": detection["quality_score"],
            "scene_type": scene_type,
        })

    stable_classes = sorted(
        [name for name, vote_count in class_presence.items() if vote_count >= max(2, len(frame_candidates) - 1)]
    )
    voted_scene_type = max(scene_type_votes.items(), key=lambda item: (item[1], item[0] == best_candidate["detection"]["analysis"]["scene_type"]))[0]
    voted_risk_level = max(risk_level_votes.items(), key=lambda item: (item[1], item[0] == best_candidate["detection"]["analysis"]["risk_level"]))[0]

    # 综合所有帧的结果计算最终评分
    max_risk_score = max(risk_scores) if risk_scores else 0
    avg_quality_score = round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0
    total_detections_across_frames = total_count_sum  # 所有帧的总检测数
    max_total_count = max(item["total_count"] for item in all_frame_detections) if all_frame_detections else 0

    aggregated_analysis = dict(best_candidate["detection"]["analysis"])
    aggregated_analysis["scene_type"] = voted_scene_type
    aggregated_analysis["risk_level"] = voted_risk_level
    # 使用所有帧中的最高风险分作为最终风险分
    aggregated_analysis["risk_score"] = round(max_risk_score, 1)
    aggregated_analysis["summary"] = (
        f"{best_candidate['detection']['analysis']['summary']}"
        f" 视频多帧分析共参考 {len(frame_candidates)} 帧，稳定类别包括："
        f"{'、'.join(stable_classes) if stable_classes else '暂无稳定类别'}，"
        f"帧间最高检测数 {max_total_count} 个。"
    )
    # 连续帧时序分析使用的帧数（锚点帧±2帧，共5帧）
    temporal_frames_count = VIDEO_CONTEXT_RADIUS * 2 + 1  # 5帧
    aggregated_analysis["video_consensus"] = {
        "frames_used": 3,  # 时序分析参考的帧数（3帧）
        "sampling_frames_used": len(frame_candidates),  # 抽帧采样总帧数
        "stable_classes": stable_classes,
        "scene_type_votes": scene_type_votes,
        "risk_level_votes": risk_level_votes,
        "average_quality_score": avg_quality_score,
        "average_total_count": round(total_count_sum / len(frame_candidates), 2) if frame_candidates else 0,
        "max_total_count": max_total_count,
        "total_detections_across_frames": total_detections_across_frames,
        "all_frame_detections": all_frame_detections,
    }

    aggregated_detection = dict(best_candidate["detection"])
    aggregated_detection["analysis"] = aggregated_analysis
    aggregated_detection["class_count"] = class_count_peak
    # 使用所有帧的平均质量分
    aggregated_detection["quality_score"] = avg_quality_score
    aggregated_detection["video_consensus"] = aggregated_analysis["video_consensus"]
    return aggregated_detection, best_candidate, top_candidates


def extract_context_frames(video_path, output_prefix, anchor_frame_index, fps, total_frames):
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        return []

    stride = max(1, int(round((fps or 1) * VIDEO_CONTEXT_STRIDE_SECONDS)))
    frame_indices = []
    # 提取 anchor_frame_index 前后各 VIDEO_CONTEXT_RADIUS 帧
    # offset: -2, -1, 0, 1, 2（共5帧：anchor前2帧、anchor、anchor后2帧）
    for offset in range(-VIDEO_CONTEXT_RADIUS, VIDEO_CONTEXT_RADIUS + 1):
        frame_index = int(anchor_frame_index + offset * stride)
        frame_index = max(0, min(max(total_frames - 1, 0), frame_index))
        if frame_index not in frame_indices:
            frame_indices.append(frame_index)

    context_frames = []
    for local_index, frame_index in enumerate(frame_indices):
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = capture.read()
        if not ok or frame is None:
            continue
        frame_name = f"{output_prefix}_context{local_index + 1}_f{frame_index}.jpg"
        frame_path = UPLOAD_DIR / frame_name
        cv2.imwrite(str(frame_path), frame)
        context_frames.append(
            {
                "frame_index": frame_index,
                "timestamp_ms": round((frame_index / fps) * 1000, 2) if fps else None,
                "path": frame_path,
                "source_image_url": build_upload_url(frame_name),
            }
        )

    capture.release()
    return context_frames


def vehicle_observations_from_detection(frame_info, detection):
    observations = []
    image_width = max(1, detection.get("image_width") or 1)
    image_height = max(1, detection.get("image_height") or 1)
    for vehicle in detection["analysis"].get("vehicle_positions", []):
        box = vehicle["box"]
        center = center_of_box(box)
        observations.append(
            {
                "frame_index": frame_info["frame_index"],
                "timestamp_ms": frame_info.get("timestamp_ms"),
                "class_name": vehicle["class_name"],
                "confidence": vehicle["confidence"],
                "box": box,
                "center": {"x": round(center[0], 2), "y": round(center[1], 2)},
                "ground_point": vehicle["ground_point"],
                "road_position": vehicle["road_position"],
                "normalized_center": {
                    "x": round(center[0] / image_width, 4),
                    "y": round(center[1] / image_height, 4),
                },
            }
        )
    return observations


def all_observations_from_detection(frame_info, detection):
    """
    收集该帧的所有观测数据，包括车辆、行人等所有可能存在危险的实体。
    """
    observations = []
    image_width = max(1, detection.get("image_width") or 1)
    image_height = max(1, detection.get("image_height") or 1)
    analysis = detection.get("analysis", {})
    roads = [item for item in detection.get("scene_detections", []) if item.get("class_name") == "road_area"]
    
    # 1. 收集车辆观测
    for vehicle in analysis.get("vehicle_positions", []):
        box = vehicle["box"]
        center = center_of_box(box)
        ground_point = vehicle.get("ground_point", bottom_center_of_box(box))
        road_position = vehicle.get("road_position", {})
        observations.append({
            "frame_index": frame_info["frame_index"],
            "timestamp_ms": frame_info.get("timestamp_ms"),
            "type": "vehicle",
            "class_name": vehicle["class_name"],
            "confidence": vehicle["confidence"],
            "box": box,
            "center": {"x": round(center[0], 2), "y": round(center[1], 2)},
            "ground_point": ground_point,
            "road_position": road_position,
            "normalized_center": {
                "x": round(center[0] / image_width, 4),
                "y": round(center[1] / image_height, 4),
            },
        })
    
    # 2. 收集行人观测（来自细粒度检测）
    for person in detection.get("fine_detections", []):
        if not is_fine_person(person):
            continue
        box = person["box"]
        center = center_of_box(box)
        ground_point = bottom_center_of_box(box)
        # 判断行人是否在道路外
        road_position = {"inside_road": False, "zone": "unknown"}
        for road in roads:
            if "mask" in road:
                if point_in_polygon(ground_point, road["mask"]):
                    road_position = {"inside_road": True, "zone": "road"}
                    break
            elif point_in_box(ground_point, road["box"]):
                road_position = {"inside_road": True, "zone": "road"}
                break
        observations.append({
            "frame_index": frame_info["frame_index"],
            "timestamp_ms": frame_info.get("timestamp_ms"),
            "type": "person",
            "class_name": person["class_name"],
            "confidence": person["confidence"],
            "box": box,
            "center": {"x": round(center[0], 2), "y": round(center[1], 2)},
            "ground_point": ground_point,
            "road_position": road_position,
            "normalized_center": {
                "x": round(center[0] / image_width, 4),
                "y": round(center[1] / image_height, 4),
            },
        })
    
    return observations


def analyze_all_temporal_behaviors(frame_observations, image_width, image_height):
    """
    综合分析所有帧中的危险行为，包括：
    1. 车辆越界行为
    2. 行人危险行为（道路外）
    3. 异常聚集行为
    """
    # 1. 跟踪车辆轨迹
    vehicle_tracks = track_vehicle_observations(frame_observations, image_width, image_height)
    vehicle_summary = summarize_vehicle_tracks(vehicle_tracks)
    
    # 2. 分析行人危险行为
    person_danger_analysis = analyze_person_temporal_behavior(frame_observations, image_width, image_height)
    
    # 3. 综合评分：取所有行为中的最高分
    all_scores = []
    if vehicle_summary.get("module"):
        all_scores.append(vehicle_summary["module"]["score"])
    if person_danger_analysis.get("module"):
        all_scores.append(person_danger_analysis["module"]["score"])
    
    combined_score = max(all_scores) if all_scores else 0
    
    # 4. 生成综合分析报告
    risks = []
    if vehicle_summary.get("persistent_offroad_track_count", 0) > 0:
        risks.append(f"车辆持续越界{vehicle_summary['persistent_offroad_track_count']}条")
    if vehicle_summary.get("edge_track_count", 0) > 0:
        risks.append(f"车辆边缘行驶{vehicle_summary['edge_track_count']}条")
    if person_danger_analysis.get("offroad_person_tracks", 0) > 0:
        risks.append(f"行人道路外活动{person_danger_analysis['offroad_person_tracks']}条")
    
    if risks:
        status = module_status(combined_score)
        reason = f"短时序分析发现以下危险行为：{'；'.join(risks)}。"
        suggestion = "建议结合原视频复核上述异常行为，确认是否存在真正的违规或危险情况。"
    else:
        status = "正常"
        reason = "短时序分析未发现明显的违规或危险行为。"
        suggestion = "当前视频片段各目标行为整体正常，可作为正常巡检记录。"
    
    return {
        "vehicle_tracks": vehicle_tracks,
        "vehicle_summary": vehicle_summary,
        "person_danger": person_danger_analysis,
        "combined_score": round(combined_score, 1),
        "tracks": vehicle_tracks,
        "persistent_offroad_track_count": vehicle_summary.get("persistent_offroad_track_count", 0),
        "lane_change_track_count": vehicle_summary.get("lane_change_track_count", 0),
        "edge_track_count": vehicle_summary.get("edge_track_count", 0),
        "module": {
            "key": "video_temporal_behavior",
            "title": "视频时序危险行为分析",
            "status": status,
            "score": round(combined_score, 1),
            "reason": reason,
            "suggestion": suggestion,
            "details": {
                "vehicle_offroad": vehicle_summary.get("persistent_offroad_track_count", 0),
                "vehicle_edge": vehicle_summary.get("edge_track_count", 0),
                "vehicle_lane_change": vehicle_summary.get("lane_change_track_count", 0),
                "person_offroad": person_danger_analysis.get("offroad_person_tracks", 0),
            }
        },
    }


def analyze_person_temporal_behavior(frame_observations, image_width, image_height):
    """
    分析行人的时序危险行为：
    - 道路外行走
    """
    # 收集所有帧中的行人观测
    all_person_obs = []
    for frame_obs in frame_observations:
        for obs in frame_obs.get("observations", []):
            if obs.get("type") == "person":
                all_person_obs.append({
                    "frame_index": frame_obs["frame_index"],
                    "timestamp_ms": frame_obs.get("timestamp_ms"),
                    "ground_point": obs.get("ground_point"),
                    "road_position": obs.get("road_position", {}),
                    "confidence": obs.get("confidence", 0),
                })
    
    if not all_person_obs:
        return {
            "offroad_person_tracks": 0,
            "module": None
        }
    
    # 简单的轨迹跟踪（按位置分组）
    offroad_person_count = 0
    
    # 统计在道路外的行人帧数
    offroad_frames = sum(1 for obs in all_person_obs if not obs["road_position"].get("inside_road", False))
    
    # 如果行人连续多帧在道路外，视为危险行为
    if offroad_frames >= 2:
        offroad_person_count = 1  # 至少有1条危险轨迹
    
    score = min(80, offroad_person_count * 40)
    
    if offroad_person_count > 0:
        status = module_status(score)
        reason = f"发现{offroad_person_count}条行人持续在道路外行走的轨迹"
        suggestion = "行人道路外行走存在安全隐患，建议现场复核。"
    else:
        status = "正常"
        reason = "未发现行人危险行为。"
        suggestion = "行人活动整体正常。"
    
    return {
        "offroad_person_tracks": offroad_person_count,
        "total_person_observations": len(all_person_obs),
        "module": {
            "key": "video_temporal_person",
            "title": "行人时序行为分析",
            "status": status,
            "score": round(score, 1),
            "reason": reason,
            "suggestion": suggestion,
        }
    }


def track_vehicle_observations(frame_observations, image_width, image_height):
    tracks = []
    max_distance = max(image_width, image_height, 1) * TRACK_MAX_DISTANCE_RATIO

    for frame in sorted(frame_observations, key=lambda item: item["frame_index"]):
        used_track_indexes = set()
        for observation in frame["observations"]:
            # 只跟踪车辆类型的观测
            if observation.get("type") != "vehicle":
                continue
            obs_center = observation["center"]
            best_index = None
            best_distance = None

            for track_index, track in enumerate(tracks):
                if track_index in used_track_indexes:
                    continue
                last = track["observations"][-1]
                if frame["frame_index"] == last["frame_index"]:
                    continue
                dx = obs_center["x"] - last["center"]["x"]
                dy = obs_center["y"] - last["center"]["y"]
                distance = float((dx * dx + dy * dy) ** 0.5)
                if distance <= max_distance and (best_distance is None or distance < best_distance):
                    best_index = track_index
                    best_distance = distance

            if best_index is None:
                tracks.append({"track_id": len(tracks) + 1, "observations": [observation]})
            else:
                tracks[best_index]["observations"].append(observation)
                used_track_indexes.add(best_index)

    return [track for track in tracks if len(track["observations"]) >= 2]


def summarize_vehicle_tracks(tracks):
    persistent_offroad = []
    lane_change_tracks = []
    edge_tracks = []

    for track in tracks:
        observations = track["observations"]
        zones = [obs["road_position"]["zone"] for obs in observations]
        offroad_count = sum(1 for zone in zones if zone == "outside")
        edge_count = sum(1 for zone in zones if zone in {"left_edge", "right_edge"})
        inside_zones = [zone for zone in zones if zone not in {"outside", "unknown"}]
        lane_zone_changes = sum(
            1 for before, after in zip(inside_zones, inside_zones[1:])
            if before != after
        )

        track["summary"] = {
            "frames": len(observations),
            "zones": zones,
            "offroad_count": offroad_count,
            "edge_count": edge_count,
            "lane_zone_changes": lane_zone_changes,
            "first_zone": zones[0] if zones else "unknown",
            "last_zone": zones[-1] if zones else "unknown",
        }

        if offroad_count >= 2:
            persistent_offroad.append(track)
        elif lane_zone_changes >= 1 and offroad_count == 0:
            lane_change_tracks.append(track)
        elif edge_count >= 2:
            edge_tracks.append(track)

    score = min(90, len(persistent_offroad) * 35 + len(edge_tracks) * 18)
    if lane_change_tracks and not persistent_offroad:
        score = min(score, 25)

    if persistent_offroad:
        status = module_status(score)
        reason = f"短时序跟踪发现 {len(persistent_offroad)} 条车辆轨迹连续处于道路外，越界可信度较高。"
        suggestion = "建议结合原视频复核这些持续越界轨迹，并优先查看是否进入人行道、绿化带、施工区。"
    elif edge_tracks:
        status = module_status(score)
        reason = f"短时序跟踪发现 {len(edge_tracks)} 条车辆轨迹连续贴近道路边缘，存在疑似越界或靠边停留风险。"
        suggestion = "建议复核道路边缘轨迹；若轨迹仍在道路 mask 内且方向连续，可按正常靠边或变道处理。"
    elif lane_change_tracks:
        status = "疑似变道"
        reason = f"短时序跟踪发现 {len(lane_change_tracks)} 条车辆轨迹在道路内部横向区域变化，未持续离开道路。"
        suggestion = "车辆在道路内部从左/中/右区域变化时，更适合判定为变道，不应直接视为越界异常。"
    else:
        status = "正常"
        reason = "短时序跟踪未发现持续越界车辆轨迹。"
        suggestion = "当前视频片段车辆轨迹整体稳定，可作为正常巡检记录。"

    return {
        "tracks": tracks,
        "persistent_offroad_track_count": len(persistent_offroad),
        "lane_change_track_count": len(lane_change_tracks),
        "edge_track_count": len(edge_tracks),
        "module": {
            "key": "video_temporal_vehicle",
            "title": "车辆短时序行为分析",
            "status": status,
            "score": round(score, 1),
            "reason": reason,
            "suggestion": suggestion,
        },
    }


def analyze_video_context(video_path, output_prefix, anchor_frame_index, fps, total_frames, detection_mode):
    context_frames = extract_context_frames(
        video_path,
        output_prefix,
        anchor_frame_index,
        fps,
        total_frames,
    )
    frame_observations = []
    image_width = 1
    image_height = 1

    for frame in context_frames:
        detection = run_detection_pipeline(frame["path"], detection_mode)
        image_width = detection.get("image_width") or image_width
        image_height = detection.get("image_height") or image_height
        
        # 收集该帧的所有观测数据
        observations = all_observations_from_detection(frame, detection)
        
        frame_observations.append(
            {
                "frame_index": frame["frame_index"],
                "timestamp_ms": frame["timestamp_ms"],
                "source_image_url": frame["source_image_url"],
                "total_count": len(detection["detections"]),
                "vehicle_count": detection["analysis"]["metrics"]["vehicle_count"],
                "person_count": detection["analysis"]["metrics"].get("person_count", 0),
                "observations": observations,
                "detection": detection,
            }
        )

    # 综合分析所有危险行为
    behavior_summary = analyze_all_temporal_behaviors(frame_observations, image_width, image_height)
    return {
        "anchor_frame_index": anchor_frame_index,
        "context_radius": VIDEO_CONTEXT_RADIUS,
        "context_stride_seconds": VIDEO_CONTEXT_STRIDE_SECONDS,
        "frames": frame_observations,
        **behavior_summary,
    }


def apply_temporal_context_to_detection(detection_data, temporal_context):
    if not temporal_context:
        return detection_data

    analysis = dict(detection_data["analysis"])
    modules = list(analysis.get("modules") or [])
    temporal_module = temporal_context["module"]
    modules.append(temporal_module)
    analysis["modules"] = modules

    # 综合评分：结合单帧评分和连续帧评分
    # 单帧风险分权重 40%，连续帧评分权重 60%
    frame_risk_score = analysis.get("risk_score", 0)
    temporal_risk_score = temporal_context.get("combined_score", temporal_module.get("score", 0))
    combined_risk_score = round(frame_risk_score * 0.4 + temporal_risk_score * 0.6, 1)
    analysis["risk_score"] = combined_risk_score
    analysis["risk_level"] = risk_score_to_level(combined_risk_score)

    # 保留单帧和连续帧的分值信息
    analysis["frame_risk_score"] = frame_risk_score
    analysis["temporal_risk_score"] = temporal_risk_score
    
    # 保存完整的时序分析结果到 analysis 中
    analysis["temporal_context"] = {
        "persistent_offroad_track_count": temporal_context.get("persistent_offroad_track_count", 0),
        "lane_change_track_count": temporal_context.get("lane_change_track_count", 0),
        "edge_track_count": temporal_context.get("edge_track_count", 0),
        "offroad_person_tracks": temporal_context.get("person_danger", {}).get("offroad_person_tracks", 0),
        "frames_used": len(temporal_context.get("frames", [])),
        "tracks_used": len(temporal_context.get("tracks", [])),
        "combined_score": temporal_context.get("combined_score", 0),
        # 包含完整的 module 信息，供前端显示
        "module": temporal_module,
        "details": temporal_module.get("details", {}),
    }
    analysis["summary"] = f"{analysis['summary']} {temporal_module['reason']}"
    analysis["metrics"] = {
        **analysis.get("metrics", {}),
        "persistent_offroad_track_count": temporal_context.get("persistent_offroad_track_count", 0),
        "lane_change_track_count": temporal_context.get("lane_change_track_count", 0),
        "edge_track_count": temporal_context.get("edge_track_count", 0),
    }

    detection_data["analysis"] = analysis
    detection_data["video_temporal_context"] = temporal_context
    return detection_data


def draw_detection_result(image_path, output_path, detections):
    image = cv2.imread(str(image_path))
    if image is None:
        return

    colors = {
        "scene": (65, 180, 75),
        "fine_target": (245, 134, 52),
    }

    for item in detections:
        box = item["box"]
        # 支持列表 [x1,y1,x2,y2] 或字典 {"x1":...,"y1":...,"x2":...,"y2":...}
        if isinstance(box, dict):
            x1, y1, x2, y2 = [int(box[key]) for key in ("x1", "y1", "x2", "y2")]
        else:
            x1, y1, x2, y2 = [int(v) for v in box]
        color = colors.get(item.get("model_role"), (255, 255, 255))
        label = f"{item['class_name']} {item['confidence']:.2f}"

        polygon = (item.get("mask") or {}).get("polygon") or []
        if len(polygon) >= 3:
            contour = np.asarray(polygon, dtype=np.int32)
            overlay = image.copy()
            cv2.fillPoly(overlay, [contour], color)
            image = cv2.addWeighted(overlay, 0.18, image, 0.82, 0)
            cv2.polylines(image, [contour], True, color, 2)

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        label_y = max(y1 - 8, 16)
        cv2.putText(
            image,
            label,
            (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA,
        )

    cv2.imwrite(str(output_path), image)


def risk_score_to_level(score):
    if score >= 75:
        return "高风险"
    if score >= 45:
        return "中风险"
    if score >= 20:
        return "低风险"
    return "正常"


def module_status(score):
    if score >= 70:
        return "严重异常"
    if score >= 45:
        return "中度异常"
    if score >= 20:
        return "轻微异常"
    return "正常"


def classify_lateral_zone(ratio):
    if ratio < 0.18:
        return "left_edge"
    if ratio < 0.38:
        return "left_lane"
    if ratio <= 0.62:
        return "center_lane"
    if ratio <= 0.82:
        return "right_lane"
    return "right_edge"


def road_position_label(zone):
    return {
        "left_edge": "道路左侧边缘",
        "left_lane": "道路左侧车道",
        "center_lane": "道路中部车道",
        "right_lane": "道路右侧车道",
        "right_edge": "道路右侧边缘",
        "outside": "道路外",
        "unknown": "未知区域",
    }.get(zone, zone)


def vehicle_road_position(vehicle, roads, image_width, image_height):
    vehicle_box = vehicle["box"]
    vehicle_area = max(1, box_area(vehicle_box))
    ground_point = bottom_center_of_box(vehicle_box)
    best_match = None

    for road_index, road in enumerate(roads):
        road_box = road["box"]
        match_method = ""
        matched = False
        overlap_ratio = intersection_area(vehicle_box, road_box) / vehicle_area

        if point_in_detection_mask(ground_point, road):
            matched = True
            match_method = "mask"
        elif "mask" in road:
            max_distance = max(image_width, image_height) * 0.01
            if point_near_detection_mask(ground_point, road, max_distance):
                matched = True
                match_method = "mask_near"
        elif overlap_ratio >= 0.15 or point_in_box(ground_point, road_box):
            matched = True
            match_method = "box"

        if not matched and overlap_ratio < 0.25:
            continue

        road_width = max(1, road_box["x2"] - road_box["x1"])
        lateral_ratio = min(1.0, max(0.0, (ground_point[0] - road_box["x1"]) / road_width))
        zone = classify_lateral_zone(lateral_ratio)
        candidate = {
            "inside_road": matched,
            "match_method": match_method or "box_overlap",
            "road_index": road_index,
            "zone": zone,
            "zone_label": road_position_label(zone),
            "lateral_ratio": round(lateral_ratio, 3),
            "overlap_ratio": round(overlap_ratio, 3),
            "edge_proximity": round(min(lateral_ratio, 1.0 - lateral_ratio), 3),
        }
        if best_match is None or candidate["overlap_ratio"] > best_match["overlap_ratio"]:
            best_match = candidate

    if best_match:
        return best_match

    return {
        "inside_road": False,
        "match_method": "none",
        "road_index": None,
        "zone": "outside",
        "zone_label": road_position_label("outside"),
        "lateral_ratio": None,
        "overlap_ratio": 0.0,
        "edge_proximity": None,
    }


def vehicle_position_summary(vehicle_positions):
    zone_count = {}
    for item in vehicle_positions:
        zone = item["road_position"]["zone"]
        zone_count[zone] = zone_count.get(zone, 0) + 1

    return {
        "zone_count": zone_count,
        "edge_vehicle_count": sum(
            1 for item in vehicle_positions
            if item["road_position"]["zone"] in {"left_edge", "right_edge"}
        ),
        "outside_vehicle_count": sum(
            1 for item in vehicle_positions
            if item["road_position"]["zone"] == "outside"
        ),
    }


def analyze_scene(detections, class_count, image_width, image_height, fine_detections=None):
    fine_detections = fine_detections or []
    all_detections = detections + fine_detections
    image_area = max(1, image_width * image_height)
    groups = {}
    for item in detections:
        groups.setdefault(item["class_name"], []).append(item)

    scene_vehicles = groups.get("vehicle", [])
    fine_vehicles = [item for item in fine_detections if is_fine_vehicle(item)]
    fine_people = [item for item in fine_detections if is_fine_person(item)]
    vehicles = fine_vehicles if fine_vehicles else scene_vehicles
    roads = groups.get("road_area", [])
    # 过滤低置信度的植被检测，减少误判
    trees = [item for item in groups.get("tree", []) if item.get("confidence", 0) >= TREE_MIN_CONFIDENCE]
    buildings = groups.get("building", [])

    area_ratio = {}
    for name, items in groups.items():
        total_area = sum(item["area"] for item in items)
        area_ratio[name] = round(min(total_area / image_area, 1) * 100, 2)

    scene_tags = []
    if roads:
        scene_tags.append("道路区域")
    if vehicles:
        scene_tags.append("车辆活动")
    if buildings:
        scene_tags.append("建筑区域")
    if trees:
        scene_tags.append("植被覆盖")

    road_ratio = area_ratio.get("road_area", 0)
    vehicle_count = len(vehicles)
    building_ratio = area_ratio.get("building", 0)
    tree_ratio = area_ratio.get("tree", 0)

    if vehicle_count >= 12 and road_ratio >= 15:
        scene_type = "交通车辆密集场景"
    elif road_ratio >= 20 and (vehicle_count > 0 or building_ratio > 5):
        scene_type = "城市道路巡检场景"
    elif building_ratio >= 20:
        scene_type = "建筑密集巡检场景"
    elif tree_ratio >= 25:
        scene_type = "绿地植被巡检场景"
    elif detections:
        scene_type = "混合航拍巡检场景"
    else:
        scene_type = "未识别到明确巡检场景"

    vehicle_positions = []
    offroad_vehicles = []
    road_vehicle_count = 0
    road_match_method_count = {"mask": 0, "mask_near": 0, "box": 0, "box_overlap": 0}
    for vehicle in vehicles:
        ground_point = bottom_center_of_box(vehicle["box"])
        road_position = vehicle_road_position(vehicle, roads, image_width, image_height)
        vehicle["ground_point"] = {
            "x": round(ground_point[0], 2),
            "y": round(ground_point[1], 2),
        }
        vehicle["road_position"] = road_position

        vehicle_positions.append(
            {
                "class_name": vehicle["class_name"],
                "confidence": vehicle["confidence"],
                "box": vehicle["box"],
                "ground_point": vehicle["ground_point"],
                "road_position": road_position,
            }
        )

        if road_position["inside_road"]:
            road_vehicle_count += 1
            match_method = road_position["match_method"]
            road_match_method_count[match_method] = road_match_method_count.get(match_method, 0) + 1
        else:
            offroad_vehicles.append(vehicle)

    has_road_masks = any("mask" in road for road in roads)
    match_description = "道路分割区域" if has_road_masks else "道路检测框"
    position_summary = vehicle_position_summary(vehicle_positions)
    edge_vehicle_count = position_summary["edge_vehicle_count"]

    offroad_count = len(offroad_vehicles)
    if vehicle_count and roads:
        offroad_rate = offroad_count / vehicle_count          # 越界车辆占比
        edge_rate = edge_vehicle_count / vehicle_count        # 边缘车辆占比
        # 只有越界率超过 20% 时才开始累积越界分，避免少量绝对数触发高分
        offroad_rate_score = max(0.0, (offroad_rate - 0.20) / 0.80) * 55
        # 单辆越界仅在越界率也偏高时才有额外加成，防止误检单辆就拉满分
        offroad_abs_score = min(20.0, offroad_count * 4) if offroad_rate >= 0.20 else min(10.0, offroad_count * 2)
        edge_score = min(15.0, edge_rate * 30) if offroad_count == 0 else min(10.0, edge_rate * 20)
        vehicle_score = min(90, offroad_rate_score + offroad_abs_score + edge_score)
        vehicle_reason = (
            f"共检测到 {vehicle_count} 个车辆目标，其中 {offroad_count} 个未落入{match_description}"
            f"（越界率 {offroad_rate:.0%}），{edge_vehicle_count} 个位于道路边缘区域。"
        )
        if has_road_masks:
            vehicle_reason += (
                f"道路内车辆中 {road_match_method_count['mask']} 个由车辆底部中心点匹配到道路 mask。"
            )
        vehicle_suggestion = (
            "建议优先复核越界率较高的区域；若只是在道路左右车道间移动，通常应按变道而非越界处理。"
            if offroad_rate >= 0.20 or edge_vehicle_count >= 2
            else "车辆目标主要位于道路中部或车道区域内，越界率处于正常范围，无需重点复核。"
        )
    elif vehicle_count and not roads:
        # 无道路参考时不直接给高分，避免误判
        vehicle_score = 15
        vehicle_reason = f"检测到 {vehicle_count} 个车辆目标，但未检测到道路区域，无法完成车辆-道路匹配。"
        vehicle_suggestion = "建议使用更清晰的道路航拍图复核，或降低道路区域检测阈值。"
    else:
        vehicle_score = 0
        vehicle_reason = "未检测到车辆目标。"
        vehicle_suggestion = "当前图像无需进行车辆越界复核。"

    # 交通密度：结合道路占比、车辆密度指数和越界情况综合评分
    if roads and road_ratio > 0:
        # 单位道路面积上的车辆密度
        density_index = vehicle_count / road_ratio * 10
        # 道路内实际承载密度（去掉越界后的有效利用率）
        road_utilization = road_vehicle_count / max(road_ratio, 1) * 10
        density_score = min(50.0, density_index * 6)
        utilization_score = min(25.0, road_utilization * 4)
        # 越界率高说明道路本身已超饱和
        congestion_bonus = min(15.0, offroad_count / max(vehicle_count, 1) * 30) if vehicle_count else 0
        traffic_score = min(85, density_score + utilization_score + congestion_bonus)
        traffic_reason = (
            f"道路区域占比约 {road_ratio:.1f}%，检测到车辆 {vehicle_count} 个"
            f"（道路内 {road_vehicle_count} 个，越界 {offroad_count} 个），"
            f"道路密度指数 {density_index:.1f}。"
        )
    elif roads and road_ratio == 0:
        traffic_score = min(30, vehicle_count * 3)
        traffic_reason = f"检测到道路区域但占比极小，当前车辆数量为 {vehicle_count} 个。"
    else:
        # 无道路时不依赖车辆数量触发高分
        traffic_score = 0
        traffic_reason = f"未检测到道路区域，无法评估交通密度（当前车辆数 {vehicle_count}）。"

    traffic_suggestion = (
        "建议进行交通密度复核，当前道路利用率较高，必要时结合连续帧分析拥堵趋势。"
        if traffic_score >= 45
        else "当前道路密度处于正常范围。"
    )

    low_conf_count = len([item for item in all_detections if item["confidence"] < 0.4])
    if all_detections:
        low_conf_rate = low_conf_count / len(all_detections)
        confidence_score = 35 if low_conf_rate >= 0.35 else 15 if low_conf_rate >= 0.2 else 0
        confidence_reason = (
            f"检测目标中有 {low_conf_count} 个置信度低于 40%，低置信度占比 {low_conf_rate:.0%}。"
        )
        confidence_suggestion = (
            "建议提高图像清晰度或使用更高 imgsz 重新检测。"
            if confidence_score else "检测结果置信度整体较稳定。"
        )
    else:
        confidence_score = 25
        confidence_reason = "本次未检测到目标，无法形成稳定场景判断。"
        confidence_suggestion = "建议更换更清晰的航拍图片或降低置信度阈值复测。"

    modules = [
        {
            "key": "vehicle_offroad",
            "title": "车辆越界异常",
            "status": module_status(vehicle_score),
            "score": round(vehicle_score, 1),
            "reason": vehicle_reason,
            "suggestion": vehicle_suggestion,
        },
        {
            "key": "traffic_density",
            "title": "道路交通密度异常",
            "status": module_status(traffic_score),
            "score": round(traffic_score, 1),
            "reason": traffic_reason,
            "suggestion": traffic_suggestion,
        },
        {
            "key": "confidence",
            "title": "检测可信度提醒",
            "status": module_status(confidence_score),
            "score": round(confidence_score, 1),
            "reason": confidence_reason,
            "suggestion": confidence_suggestion,
        },
    ]

    overall_score = max(module["score"] for module in modules) if modules else 0
    risk_level = risk_score_to_level(overall_score)
    active_modules = [module for module in modules if module["score"] >= 20]
    if active_modules:
        key_points = "；".join(f"{module['title']}：{module['status']}" for module in active_modules)
    else:
        key_points = "各异常模块暂未发现明显风险"

    summary = (
        f"综合判断，该图像属于{scene_type}。"
        f"系统识别到 {len(all_detections)} 个目标，主要场景标签包括："
        f"{'、'.join(scene_tags) if scene_tags else '暂无明确标签'}。"
        f"当前综合风险等级为{risk_level}，{key_points}。"
    )

    return {
        "scene_type": scene_type,
        "risk_level": risk_level,
        "risk_score": round(overall_score, 1),
        "scene_tags": scene_tags,
        "area_ratio": area_ratio,
        "metrics": {
            "vehicle_count": vehicle_count,
            "fine_vehicle_count": len(fine_vehicles),
            "person_count": len(fine_people),
            "road_vehicle_count": road_vehicle_count,
            "offroad_vehicle_count": offroad_count,
            "road_mask_vehicle_count": road_match_method_count["mask"],
            "road_box_vehicle_count": road_match_method_count["box"],
            "road_edge_vehicle_count": edge_vehicle_count,
            "road_position_zone_count": position_summary["zone_count"],
            "low_confidence_count": low_conf_count,
        },
        "vehicle_positions": vehicle_positions,
        "summary": summary,
        "modules": modules,
    }


@app.get("/")
def root():
    return {
        "message": "无人机航拍图像智能识别后端已启动",
        "status": "running",
        "models": {
            "scene": True,
            "visdrone": visdrone_model is not None,
        },
    }


@app.post("/detect")
async def detect_image(
    file: UploadFile = File(...),
    detection_mode: str = Form(default="fusion"),
    current_user=Depends(get_current_user),
):
    if detection_mode not in DETECTION_MODES:
        raise HTTPException(status_code=400, detail="不支持的检测模式")
    if detection_mode == "fine" and visdrone_model is None:
        raise HTTPException(status_code=503, detail="细粒度 VisDrone 模型未加载，暂不能使用细粒度检测")

    media_kind = detect_media_kind(file)

    # 生成唯一文件名，避免重复覆盖
    file_ext = Path(file.filename or "").suffix.lower()
    file_id = str(uuid.uuid4())
    upload_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    result_img_path = RESULT_DIR / f"{file_id}_result.jpg"
    result_json_path = RESULT_DIR / f"{file_id}_result.json"
    source_image_path = None
    source_image_url = None
    video_sampling = None
    video_temporal_context = None

    try:
        save_upload_file(file, upload_path)

        if media_kind == "video":
            try:
                file_size = upload_path.stat().st_size
            except OSError:
                file_size = 0
            if file_size > MAX_VIDEO_BYTES:
                size_mb = round(file_size / (1024 * 1024), 1)
                limit_mb = round(MAX_VIDEO_BYTES / (1024 * 1024), 0)
                upload_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"视频文件过大（{size_mb}MB），请压缩或裁剪到 {int(limit_mb)}MB 以内再上传",
                )

        if media_kind == "image":
            detection_data = run_detection_pipeline(upload_path, detection_mode)
            source_image_path = upload_path
            source_image_url = build_upload_url(upload_path.name)
            report = build_report(
                detection_mode,
                detection_data["scene_detections"],
                detection_data["fine_detections"],
                detection_data["detections"],
                detection_data["class_count"],
                detection_data["analysis"],
                fusion_summary=detection_data["fusion"],
            )
        else:
            best_candidate = None
            first_round_best_frame = None  # 第一轮抽帧中质量最高的帧，作为连续帧分析的锚点
            attempts = []
            video_meta = None

            for attempt_index in range(MAX_VIDEO_SAMPLING_ATTEMPTS):
                sample_count = DEFAULT_FRAME_SAMPLE_COUNT + attempt_index
                sampling_result = extract_video_frames(upload_path, file_id, attempt_index, sample_count)
                video_meta = {
                    "fps": sampling_result["fps"],
                    "total_frames": sampling_result["total_frames"],
                    "duration_ms": sampling_result["duration_ms"],
                }

                sampled_frames = []
                attempt_candidates = []
                for frame in sampling_result["frames"]:
                    frame_detection = run_detection_pipeline(frame["path"], detection_mode)
                    frame_quality_score = score_frame_quality(
                        frame_detection["detections"],
                        frame_detection["analysis"],
                        frame.get("visual_quality"),
                    )
                    frame_detection["quality_score"] = frame_quality_score
                    attempt_candidates.append(
                        {
                            "frame": frame,
                            "detection": frame_detection,
                            "attempt_index": attempt_index,
                        }
                    )
                    sampled_frames.append(
                        {
                            "frame_index": frame["frame_index"],
                            "timestamp_ms": frame["timestamp_ms"],
                            "quality_score": frame_quality_score,
                            "total_count": len(frame_detection["detections"]),
                            "risk_level": frame_detection["analysis"]["risk_level"],
                            "risk_score": frame_detection["analysis"].get("risk_score"),
                            "source_image_url": frame["source_image_url"],
                            "visual_quality": frame.get("visual_quality"),
                        }
                    )

                aggregated_detection, attempt_best_candidate, voted_candidates = aggregate_frame_detections(attempt_candidates)
                if aggregated_detection is None:
                    continue

                # 记录第一轮中质量最高的帧作为连续帧分析锚点
                if attempt_index == 0 and attempt_best_candidate is not None:
                    first_round_best_frame = attempt_best_candidate["frame"]

                candidate = {
                    "frame": attempt_best_candidate["frame"],
                    "detection": aggregated_detection,
                    "attempt_index": attempt_index,
                    "voted_frames": voted_candidates,
                }
                if best_candidate is None or candidate["detection"]["quality_score"] > best_candidate["detection"]["quality_score"]:
                    best_candidate = candidate

                this_attempt_passed = (
                    best_candidate is not None
                    and best_candidate["attempt_index"] == attempt_index
                    and best_candidate["detection"]["quality_score"] >= VIDEO_QUALITY_THRESHOLD
                )
                attempts.append(
                    {
                        "attempt": attempt_index + 1,
                        "sample_count": sample_count,
                        "candidate_count": sampling_result["candidate_count"],
                        "passed": this_attempt_passed,
                        "frames": sampled_frames,
                    }
                )

            # 无论是否达到阈值，都运行完所有轮次以获取完整的抽帧信息
            if best_candidate is None:
                raise HTTPException(status_code=400, detail="视频抽帧失败，未读取到可检测帧")

            detection_data = best_candidate["detection"]
            source_image_path = best_candidate["frame"]["path"]
            source_image_url = best_candidate["frame"]["source_image_url"]
            selected_frame = best_candidate["frame"]

            # 连续帧分析以选中的最佳帧为锚点，向前向后各检测2帧
            # 验证选中的帧是否确实存在越界或危险行为
            anchor_frame = selected_frame
            video_temporal_context = analyze_video_context(
                upload_path,
                file_id,
                anchor_frame["frame_index"],
                (video_meta or {}).get("fps", 0),
                (video_meta or {}).get("total_frames", 0),
                detection_mode,
            )
            detection_data = apply_temporal_context_to_detection(detection_data, video_temporal_context)
            video_sampling = {
                **(video_meta or {}),
                "total_attempts": len(attempts),
                "max_attempts": MAX_VIDEO_SAMPLING_ATTEMPTS,
                "quality_threshold": VIDEO_QUALITY_THRESHOLD,
                "threshold_met": detection_data["quality_score"] >= VIDEO_QUALITY_THRESHOLD,
                "selected_frame": {
                    "frame_index": selected_frame["frame_index"],
                    "timestamp_ms": selected_frame["timestamp_ms"],
                    "source_image_url": selected_frame["source_image_url"],
                    "quality_score": detection_data["quality_score"],
                },
                "consensus": detection_data.get("video_consensus"),
                "temporal_context": detection_data.get("analysis", {}).get("temporal_context"),
                "attempts": attempts,
            }
            report = build_report(
                detection_mode,
                detection_data["scene_detections"],
                detection_data["fine_detections"],
                detection_data["detections"],
                detection_data["class_count"],
                detection_data["analysis"],
                fusion_summary=detection_data["fusion"],
                media_summary=f"，视频抽帧共 {video_sampling['total_attempts']} 轮，选中第 {selected_frame['frame_index']} 帧",
                video_temporal_context=video_temporal_context,
            )
            _cleanup_video_temp_frames(file_id, keep_frame_path=source_image_path)
    except Exception:
        try:
            upload_path.unlink(missing_ok=True)
        except OSError:
            pass
        try:
            _cleanup_video_temp_frames(file_id)
        except Exception:
            pass
        raise

    try:
        scene_detections = detection_data["scene_detections"]
        fine_detections = detection_data["fine_detections"]
        detections = detection_data["detections"]
        class_count = detection_data["class_count"]
        analysis = detection_data["analysis"]
        models_used = detection_data["models_used"]

        draw_detection_result(source_image_path, result_img_path, detections)

        # 保存 JSON
        result_data = {
            "image_id": file_id,
            "original_filename": file.filename,
            "input_type": media_kind,
            "media_type_label": "视频" if media_kind == "video" else "图片",
            "detection_mode": detection_mode,
            "detection_mode_label": DETECTION_MODES[detection_mode],
            "models_used": models_used,
            "total_count": len(detections),
            "class_count": class_count,
            "detections": detections,
            "scene_detections": scene_detections,
            "fine_detections": fine_detections,
            "models": {
                "scene": {
                    "enabled": True,
                    "path": str(SCENE_MODEL_PATH),
                    "description": "自训练航拍场景模型，用于道路、建筑、树木等场景要素识别；车辆目标由细粒度模型负责。",
                },
                "visdrone": {
                    "enabled": visdrone_model is not None,
                    "path": str(VISDRONE_MODEL_PATH),
                    "description": "VisDrone 小目标检测模型，用于车辆、行人等细粒度目标识别。",
                    "error": visdrone_model_error,
                },
            },
            "source_image_url": source_image_url,
            "result_image_url": build_result_url(f"{file_id}_result.jpg"),
            "result_json_url": build_result_url(f"{file_id}_result.json"),
            "report": report,
            "analysis": analysis,
            "fusion": detection_data["fusion"],
            "video_sampling": video_sampling,
            "video_temporal_context": video_temporal_context,
        }

        with open(result_json_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

        result_data["log_id"] = create_detection_log(current_user, result_data)
        return convert_numpy_to_python(result_data)
    except Exception:
        raise
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
