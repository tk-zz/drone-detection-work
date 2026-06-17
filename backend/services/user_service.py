from __future__ import annotations

from fastapi import HTTPException

from backend.core.constants import ROLE_ADMIN, ROLE_LABELS, USER_ROLES
from backend.core.database import db_execute, db_fetchall, db_fetchone, get_db
from backend.core.security import create_session_token, create_token_expiry, hash_password, iso_now, verify_password


def validate_role(role: str):
    if role not in USER_ROLES:
        raise HTTPException(status_code=400, detail="不支持的用户角色")
    return role


def row_to_user_detail(user_row: dict):
    return {
        "id": user_row["id"],
        "username": user_row["username"],
        "role": user_row["role"],
        "role_label": ROLE_LABELS.get(user_row["role"], user_row["role"]),
        "status": int(user_row["status"]),
        "is_active": bool(user_row["status"]),
        "created_at": user_row["created_at"],
        "updated_at": user_row["updated_at"],
    }


def fetch_user_row(conn, user_id: int):
    return db_fetchone(
        conn,
        """
        SELECT id, username, role, status, created_at, updated_at
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    )


def authenticate_user(username: str, password: str):
    with get_db() as conn:
        user = db_fetchone(
            conn,
            """
            SELECT id, username, password, salt, role, status
            FROM users
            WHERE username = ?
            """,
            (username,),
        )

    if not user or not user.get("status") or not verify_password(password, user["salt"], user["password"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return user


def create_session(user_id: int):
    token = create_session_token()
    now, expires_at = create_token_expiry()
    with get_db() as conn:
        db_execute(
            conn,
            """
            INSERT INTO sessions (token, user_id, expires_at, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (token, user_id, expires_at.isoformat(), now.isoformat()),
        )
    return token, expires_at


def logout_session(token: str):
    with get_db() as conn:
        db_execute(conn, "DELETE FROM sessions WHERE token = ?", (token,))


def list_users():
    with get_db() as conn:
        rows = db_fetchall(conn, "SELECT id, username, role, status, created_at, updated_at FROM users ORDER BY created_at DESC")
    return [row_to_user_detail(row) for row in rows]


def get_user_by_id(user_id: int):
    with get_db() as conn:
        user_row = fetch_user_row(conn, user_id)
    if not user_row:
        raise HTTPException(status_code=404, detail="用户不存在")
    return row_to_user_detail(user_row)


def create_user(username: str, password: str, role: str):
    username = username.strip()
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少需要 3 个字符")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="密码至少需要 6 个字符")
    validate_role(role)

    salt, password_hash = hash_password(password)
    now = iso_now()
    try:
        with get_db() as conn:
            cursor = db_execute(
                conn,
                """
                INSERT INTO users (username, password, salt, role, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (username, password_hash, salt, role, 1, now, now),
            )
            user_row = fetch_user_row(conn, cursor.lastrowid)
    except Exception as exc:
        if "UNIQUE" in str(exc).upper() or "DUPLICATE" in str(exc).upper():
            raise HTTPException(status_code=409, detail="用户名已存在")
        raise

    return row_to_user_detail(user_row)


def update_user(user_id: int, payload: dict, current_user_id: int):
    updates = []
    params = []

    if "role" in payload and payload["role"] is not None:
        validate_role(payload["role"])
        updates.append("role = ?")
        params.append(payload["role"])

    if "status" in payload and payload["status"] is not None:
        if user_id == current_user_id and int(payload["status"]) == 0:
            raise HTTPException(status_code=400, detail="不能停用当前管理员账号")
        updates.append("status = ?")
        params.append(int(payload["status"]))

    if payload.get("password"):
        if len(payload["password"]) < 6:
            raise HTTPException(status_code=400, detail="密码至少需要 6 个字符")
        salt, password_hash = hash_password(payload["password"])
        updates.extend(["password = ?", "salt = ?"])
        params.extend([password_hash, salt])

    if not updates:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")

    updates.append("updated_at = ?")
    params.append(iso_now())
    params.append(user_id)

    with get_db() as conn:
        cursor = db_execute(conn, f"UPDATE users SET {', '.join(updates)} WHERE id = ?", tuple(params))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="用户不存在")
        user_row = fetch_user_row(conn, user_id)
    return row_to_user_detail(user_row)


def delete_user(user_id: int, current_user_id: int):
    if user_id == current_user_id:
        raise HTTPException(status_code=400, detail="不能删除当前登录管理员")
    with get_db() as conn:
        user = db_fetchone(conn, "SELECT id, role FROM users WHERE id = ?", (user_id,))
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        if user["role"] == ROLE_ADMIN:
            admin_count = db_fetchone(conn, "SELECT COUNT(*) AS count FROM users WHERE role = ? AND status = 1", (ROLE_ADMIN,))
            if admin_count and admin_count["count"] <= 1:
                raise HTTPException(status_code=400, detail="至少需要保留一个启用状态的管理员账号")
        db_execute(conn, "DELETE FROM users WHERE id = ?", (user_id,))


def change_password(user_id: int, current_password: str, new_password: str):
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="当前密码与新密码不能为空")
    if new_password == current_password:
        raise HTTPException(status_code=400, detail="新密码不能与当前密码相同")
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少需要 6 个字符")

    with get_db() as conn:
        record = db_fetchone(
            conn,
            "SELECT id, password, salt, status FROM users WHERE id = ?",
            (user_id,),
        )
        if not record:
            raise HTTPException(status_code=404, detail="用户不存在")
        if not record.get("status"):
            raise HTTPException(status_code=403, detail="账号已停用，无法修改密码")
        if not verify_password(current_password, record["salt"], record["password"]):
            raise HTTPException(status_code=400, detail="当前密码不正确")

        new_salt, new_hash = hash_password(new_password)
        db_execute(
            conn,
            "UPDATE users SET password = ?, salt = ?, updated_at = ? WHERE id = ?",
            (new_hash, new_salt, iso_now(), user_id),
        )
        db_execute(conn, "DELETE FROM sessions WHERE user_id = ?", (user_id,))

    return {"message": "密码已更新，请重新登录"}
