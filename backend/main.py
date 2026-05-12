from fastapi import Depends, FastAPI, Header, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import shutil
import secrets
import sqlite3
import uuid
import json
import os

app = FastAPI(title="无人机航拍图像智能识别后端")

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
RESULT_DIR = BASE_DIR / "results"
DB_PATH = BASE_DIR / "app.db"
TOKEN_HOURS = 12

UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

# 加载 YOLO 模型
model = YOLO("models/best.pt")

# 让浏览器可以访问检测结果图片
app.mount("/results", StaticFiles(directory=str(RESULT_DIR)), name="results")


class LoginRequest(BaseModel):
    username: str
    password: str


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return salt, digest.hex()


def verify_password(password, salt, password_hash):
    _, candidate = hash_password(password, salt)
    return hmac.compare_digest(candidate, password_hash)


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )

        user_count = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
        if user_count == 0:
            username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
            password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
            salt, password_hash = hash_password(password)
            conn.execute(
                """
                INSERT INTO users (username, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (username, password_hash, salt, datetime.now(timezone.utc).isoformat()),
            )


def create_session(user_id):
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=TOKEN_HOURS)
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO sessions (token, user_id, expires_at, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (token, user_id, expires_at.isoformat(), now.isoformat()),
        )
    return token, expires_at


def get_current_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或登录已失效")

    token = authorization.removeprefix("Bearer ").strip()
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT users.id, users.username, sessions.expires_at
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = ?
            """,
            (token,),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="未登录或登录已失效")

    expires_at = datetime.fromisoformat(row["expires_at"])
    if expires_at <= datetime.now(timezone.utc):
        with get_db() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")

    return {"id": row["id"], "username": row["username"]}


init_db()


def box_area(box):
    return max(0, box["x2"] - box["x1"]) * max(0, box["y2"] - box["y1"])


def intersection_area(box_a, box_b):
    x1 = max(box_a["x1"], box_b["x1"])
    y1 = max(box_a["y1"], box_b["y1"])
    x2 = min(box_a["x2"], box_b["x2"])
    y2 = min(box_a["y2"], box_b["y2"])
    return max(0, x2 - x1) * max(0, y2 - y1)


def center_of_box(box):
    return ((box["x1"] + box["x2"]) / 2, (box["y1"] + box["y2"]) / 2)


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


def analyze_scene(detections, class_count, image_width, image_height):
    image_area = max(1, image_width * image_height)
    groups = {}
    for item in detections:
        groups.setdefault(item["class_name"], []).append(item)

    vehicles = groups.get("vehicle", [])
    roads = groups.get("road_area", [])
    waters = groups.get("water", [])
    buildings = groups.get("building", [])
    trees = groups.get("tree", [])

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
    if waters:
        scene_tags.append("水域周边")

    road_ratio = area_ratio.get("road_area", 0)
    vehicle_count = len(vehicles)
    building_ratio = area_ratio.get("building", 0)
    tree_ratio = area_ratio.get("tree", 0)
    water_ratio = area_ratio.get("water", 0)

    if water_ratio >= 15:
        scene_type = "水域周边巡检场景"
    elif vehicle_count >= 12 and road_ratio >= 15:
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

    offroad_vehicles = []
    road_vehicle_count = 0
    for vehicle in vehicles:
        vehicle_box = vehicle["box"]
        vehicle_area = max(1, box_area(vehicle_box))
        matched = False
        for road in roads:
            road_box = road["box"]
            overlap_ratio = intersection_area(vehicle_box, road_box) / vehicle_area
            if overlap_ratio >= 0.15 or point_in_box(center_of_box(vehicle_box), road_box):
                matched = True
                break
        if matched:
            road_vehicle_count += 1
        else:
            offroad_vehicles.append(vehicle)

    offroad_count = len(offroad_vehicles)
    if vehicle_count and roads:
        offroad_rate = offroad_count / vehicle_count
        vehicle_score = min(85, offroad_count * 18 + offroad_rate * 45)
        vehicle_reason = (
            f"共检测到 {vehicle_count} 个车辆目标，其中 {offroad_count} 个未与道路区域形成有效重叠。"
        )
        vehicle_suggestion = (
            "建议复核非道路车辆位置，判断是否为停车区域、异常停放或检测框偏移。"
            if offroad_count else "车辆目标主要位于道路区域内，暂未发现明显越界车辆。"
        )
    elif vehicle_count and not roads:
        vehicle_score = 35
        vehicle_reason = f"检测到 {vehicle_count} 个车辆目标，但未检测到道路区域，无法完成车辆-道路匹配。"
        vehicle_suggestion = "建议使用更清晰的道路航拍图复核，或降低道路区域检测阈值。"
    else:
        vehicle_score = 0
        vehicle_reason = "未检测到车辆目标。"
        vehicle_suggestion = "当前图像无需进行车辆越界复核。"

    if roads:
        density_base = road_ratio if road_ratio > 0 else 1
        density_index = vehicle_count / density_base * 10
    else:
        density_index = vehicle_count * 4

    if vehicle_count >= 25 or density_index >= 7:
        traffic_score = 75
    elif vehicle_count >= 12 or density_index >= 4:
        traffic_score = 50
    elif vehicle_count >= 5:
        traffic_score = 25
    else:
        traffic_score = 0

    traffic_reason = (
        f"道路区域占比约 {road_ratio:.2f}%，检测到车辆 {vehicle_count} 个，道路内车辆 {road_vehicle_count} 个。"
        if roads else f"未检测到道路区域，当前车辆数量为 {vehicle_count}。"
    )
    traffic_suggestion = (
        "建议进行交通密度复核，必要时结合连续帧分析拥堵趋势。"
        if traffic_score >= 45 else "当前车辆数量未达到明显拥堵阈值。"
    )

    water_near_vehicle = 0
    if waters:
        margin_x = image_width * 0.04
        margin_y = image_height * 0.04
        for vehicle in vehicles:
            center = center_of_box(vehicle["box"])
            if any(point_in_box(center, expanded_box(water["box"], margin_x, margin_y)) for water in waters):
                water_near_vehicle += 1

    if waters and water_near_vehicle:
        water_score = min(80, 35 + water_near_vehicle * 15)
        water_reason = f"检测到水域区域，且有 {water_near_vehicle} 个车辆目标位于水域邻近范围。"
        water_suggestion = "建议对水域周边车辆活动进行人工复核，关注临水道路或停车风险。"
    elif waters:
        water_score = 5
        water_reason = f"检测到水域区域，水域面积占比约 {water_ratio:.2f}%，未发现车辆邻近水域。"
        water_suggestion = "当前水域周边风险较低，可作为常规巡检记录。"
    else:
        water_score = 0
        water_reason = "未检测到水域区域。"
        water_suggestion = "当前图像跳过水域异常分析。"

    low_conf_count = len([item for item in detections if item["confidence"] < 0.4])
    if detections:
        low_conf_rate = low_conf_count / len(detections)
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
            "key": "water_safety",
            "title": "水域周边风险",
            "status": module_status(water_score),
            "score": round(water_score, 1),
            "reason": water_reason,
            "suggestion": water_suggestion,
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
        f"系统识别到 {len(detections)} 个目标，主要场景标签包括："
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
            "road_vehicle_count": road_vehicle_count,
            "offroad_vehicle_count": offroad_count,
            "water_near_vehicle_count": water_near_vehicle,
            "low_confidence_count": low_conf_count,
        },
        "summary": summary,
        "modules": modules,
    }


@app.get("/")
def root():
    return {
        "message": "无人机航拍图像智能识别后端已启动",
        "status": "running"
    }


@app.post("/auth/login")
def login(payload: LoginRequest):
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, username, password_hash, salt FROM users WHERE username = ?",
            (payload.username,),
        ).fetchone()

    if not user or not verify_password(payload.password, user["salt"], user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token, expires_at = create_session(user["id"])
    return {
        "token": token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user["id"],
            "username": user["username"],
        },
    }


@app.get("/auth/me")
def me(current_user=Depends(get_current_user)):
    return {"user": current_user}


@app.post("/auth/logout")
def logout(authorization: str = Header(default="")):
    if authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        with get_db() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    return {"message": "已退出登录"}


@app.post("/detect")
async def detect_image(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    # 生成唯一文件名，避免重复覆盖
    file_ext = Path(file.filename).suffix
    file_id = str(uuid.uuid4())
    upload_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    result_img_path = RESULT_DIR / f"{file_id}_result.jpg"
    result_json_path = RESULT_DIR / f"{file_id}_result.json"

    # 保存上传图片
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # YOLO 检测
    results = model(str(upload_path), conf=0.25)

    detections = []

    image_width = 0
    image_height = 0

    for result in results:
        if result.orig_shape:
            image_height, image_width = result.orig_shape

        # 保存检测结果图片
        result.save(filename=str(result_img_path))

        for box in result.boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({
                "class_id": cls_id,
                "class_name": cls_name,
                "confidence": round(conf, 4),
                "box": {
                    "x1": round(x1, 2),
                    "y1": round(y1, 2),
                    "x2": round(x2, 2),
                    "y2": round(y2, 2)
                },
                "area": round((x2 - x1) * (y2 - y1), 2)
            })

    # 类别数量统计
    class_count = {}
    for item in detections:
        name = item["class_name"]
        class_count[name] = class_count.get(name, 0) + 1

    analysis = analyze_scene(detections, class_count, image_width, image_height)

    # 自动分析报告
    if detections:
        main_class = max(class_count, key=class_count.get)
        report = (
            f"本次图像共检测到 {len(detections)} 个目标。"
            f"其中数量最多的类别为 {main_class}，共 {class_count[main_class]} 个。"
            f"{analysis['summary']}"
        )
    else:
        report = (
            "本次图像未检测到自训练航拍场景模型可识别的目标。"
            "可能原因是图像中目标不属于当前模型类别，或目标过小、置信度较低。"
        )

    # 保存 JSON
    result_data = {
        "image_id": file_id,
        "original_filename": file.filename,
        "total_count": len(detections),
        "class_count": class_count,
        "detections": detections,
        "result_image_url": f"/results/{file_id}_result.jpg",
        "report": report,
        "analysis": analysis
    }

    with open(result_json_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    return result_data
