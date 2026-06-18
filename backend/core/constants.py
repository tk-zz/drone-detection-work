from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
MODEL_DIR = PROJECT_DIR / "models"
UPLOAD_DIR = BASE_DIR / "uploads"
RESULT_DIR = BASE_DIR / "results"

TOKEN_HOURS = 12

ROLE_NORMAL = "NORMAL"
ROLE_ADMIN = "ADMIN"
USER_ROLES = {ROLE_NORMAL, ROLE_ADMIN}

ROLE_LABELS = {
    ROLE_NORMAL: "普通用户",
    ROLE_ADMIN: "管理员",
}

DETECTION_MODES = {
    "fusion": "粗细粒度融合检测",
    "scene": "粗粒度场景检测",
    "fine": "细粒度目标检测",
}

SCENE_MODEL_PATH = MODEL_DIR / "best.pt"
VISDRONE_MODEL_PATH = MODEL_DIR / "yolov8x-visdrone.pt"

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

DEFAULT_FRAME_SAMPLE_COUNT = 3
MAX_VIDEO_SAMPLING_ATTEMPTS = 3
VIDEO_QUALITY_THRESHOLD = 45
VIDEO_PREFILTER_CANDIDATE_MULTIPLIER = 4
VIDEO_VOTING_TOP_K = 3
VIDEO_CONTEXT_RADIUS = 2  # 前后各2帧
VIDEO_CONTEXT_STRIDE_SECONDS = 0.5
TRACK_MAX_DISTANCE_RATIO = 0.045
FUSION_IOU_THRESHOLD = 0.5

MAX_VIDEO_BYTES = 200 * 1024 * 1024
MAX_VIDEO_FRAMES = 20000
MAX_VIDEO_DURATION_MS = 10 * 60 * 1000

VISDRONE_VEHICLE_CLASSES = {
    "bicycle",
    "car",
    "van",
    "truck",
    "tricycle",
    "awning-tricycle",
    "bus",
    "motor",
}
VISDRONE_PERSON_CLASSES = {"pedestrian", "people"}
SCENE_VEHICLE_CLASSES = {"vehicle"}
SCENE_PERSON_CLASSES = {"person"}

# 植被检测置信度阈值
TREE_MIN_CONFIDENCE = 0.40
