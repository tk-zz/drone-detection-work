from __future__ import annotations

import json
import numpy as np

from backend.core.constants import ROLE_ADMIN
from backend.core.database import db_execute, db_fetchall, get_db
from backend.core.security import iso_now


def row_to_detection_log(row):
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "username": row["username"],
        "image_id": row["image_id"],
        "original_filename": row["original_filename"],
        "detection_mode": row["detection_mode"],
        "detection_mode_label": row["detection_mode_label"],
        "models_used": json.loads(row["models_used"] or "[]"),
        "total_count": row["total_count"],
        "risk_level": row["risk_level"],
        "risk_score": row["risk_score"],
        "scene_type": row["scene_type"],
        "class_count": json.loads(row["class_count"] or "{}"),
        "report": row["report"],
        "result_image_url": row["result_image_url"],
        "result_json_url": row["result_json_url"],
        "created_at": row["created_at"],
    }


def list_detection_logs(current_user):
    with get_db() as conn:
        if current_user["role"] == ROLE_ADMIN:
            rows = db_fetchall(
                conn,
                """
                SELECT *
                FROM detection_logs
                ORDER BY created_at DESC
                LIMIT 200
                """,
            )
        else:
            rows = db_fetchall(
                conn,
                """
                SELECT *
                FROM detection_logs
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 100
                """,
                (current_user["id"],),
            )
    return [row_to_detection_log(row) for row in rows]


def _convert(obj):
    """递归将 numpy 类型转换为 Python 原生类型"""
    if isinstance(obj, dict):
        return {k: _convert(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_convert(item) for item in obj)
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


def create_detection_log(current_user, result_data):
    # 确保 result_data 中的 numpy 类型被转换
    result_data = _convert(result_data)
    with get_db() as conn:
        cursor = db_execute(
            conn,
            """
            INSERT INTO detection_logs (
                user_id, username, image_id, original_filename, detection_mode,
                detection_mode_label, models_used, total_count, risk_level,
                risk_score, scene_type, class_count, report, result_image_url,
                result_json_url, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                current_user["id"],
                current_user["username"],
                result_data["image_id"],
                result_data["original_filename"],
                result_data["detection_mode"],
                result_data["detection_mode_label"],
                json.dumps(result_data["models_used"], ensure_ascii=False),
                result_data["total_count"],
                result_data["analysis"]["risk_level"],
                result_data["analysis"]["risk_score"],
                result_data["analysis"]["scene_type"],
                json.dumps(result_data["class_count"], ensure_ascii=False),
                result_data["report"],
                result_data["result_image_url"],
                result_data["result_json_url"],
                iso_now(),
            ),
        )
        return cursor.lastrowid
