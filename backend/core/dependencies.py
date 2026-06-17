from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException

from backend.core.database import db_execute, db_fetchone, get_db
from backend.core.constants import ROLE_ADMIN


def get_current_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或登录已失效")

    token = authorization.removeprefix("Bearer ").strip()
    with get_db() as conn:
        row = db_fetchone(
            conn,
            """
            SELECT
                users.id,
                users.username,
                users.role,
                users.status,
                sessions.expires_at
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = ?
            """,
            (token,),
        )

    if not row or not row.get("status"):
        raise HTTPException(status_code=401, detail="未登录或登录已失效")

    expires_at = datetime.fromisoformat(row["expires_at"])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        with get_db() as conn:
            db_execute(conn, "DELETE FROM sessions WHERE token = ?", (token,))
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")

    return {
        "id": row["id"],
        "username": row["username"],
        "role": row["role"],
        "status": row["status"],
    }


def require_admin(current_user=Depends(get_current_user)):
    if current_user.get("role") != ROLE_ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user
