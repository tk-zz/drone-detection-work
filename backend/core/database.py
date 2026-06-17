from __future__ import annotations

from contextlib import contextmanager

try:
    import pymysql
    import pymysql.cursors
    pymysql.install_as_MySQLdb()
except ImportError as _pymysql_import_error:
    raise RuntimeError("使用 MySQL 需要先安装 pymysql：pip install pymysql") from _pymysql_import_error


@contextmanager
def get_db():
    from backend.core.config import get_mysql_config
    mysql_config = get_mysql_config()
    try:
        conn = pymysql.connect(**mysql_config)
    except Exception as exc:
        if "using password: NO" in str(exc):
            raise RuntimeError(
                "未读取到 MYSQL_PASSWORD。请在项目根目录或 backend/ 目录下的 .env 文件中配置，"
                "或在当前终端执行 export MYSQL_PASSWORD=<密码> 后重新启动。"
            ) from exc
        if "Access denied for user" in str(exc):
            raise RuntimeError(
                "MySQL 认证失败。"
                f" 当前生效配置：MYSQL_USER={mysql_config['user']}，"
                f"MYSQL_DATABASE={mysql_config['database']}，"
                f"MYSQL_PASSWORD={'已设置' if mysql_config['password'] else '未设置'}。"
                " 若与 .env 不一致，说明 shell 环境变量覆盖了 .env，请新开终端或先 unset 相关变量后重启。"
            ) from exc
        raise
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def db_execute(conn, sql: str, params=()):
    cursor = conn.cursor()
    cursor.execute(sql.replace("?", "%s"), params)
    return cursor


def db_fetchone(conn, sql: str, params=()):
    cursor = db_execute(conn, sql, params)
    row = cursor.fetchone()
    if row is None:
        return None
    if not isinstance(row, dict):
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))
    return row


def db_fetchall(conn, sql: str, params=()):
    cursor = db_execute(conn, sql, params)
    rows = cursor.fetchall()
    if not rows:
        return []
    if not isinstance(rows[0], dict):
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    return list(rows)


def _ensure_schema(conn):
    db_execute(conn, """
        CREATE TABLE IF NOT EXISTS users (
            id INT NOT NULL AUTO_INCREMENT,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(255) NOT NULL,
            salt VARCHAR(64) NOT NULL,
            role ENUM('NORMAL', 'ADMIN') NOT NULL DEFAULT 'NORMAL',
            status TINYINT NOT NULL DEFAULT 1,
            created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY username (username)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
    """)
    db_execute(conn, """
        CREATE TABLE IF NOT EXISTS sessions (
            token VARCHAR(128) NOT NULL,
            user_id INT NOT NULL,
            expires_at VARCHAR(40) NOT NULL,
            created_at VARCHAR(40) NOT NULL,
            PRIMARY KEY (token),
            CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
    """)
    db_execute(conn, """
        CREATE TABLE IF NOT EXISTS detection_logs (
            id INT NOT NULL AUTO_INCREMENT,
            user_id INT NOT NULL,
            username VARCHAR(80) NOT NULL,
            image_id VARCHAR(80) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            detection_mode VARCHAR(40) NOT NULL,
            detection_mode_label VARCHAR(80) NOT NULL,
            models_used TEXT NOT NULL,
            total_count INT NOT NULL,
            risk_level VARCHAR(40) NOT NULL,
            risk_score DOUBLE NOT NULL,
            scene_type VARCHAR(80) NOT NULL,
            class_count TEXT NOT NULL,
            report TEXT NOT NULL,
            result_image_url VARCHAR(255) NOT NULL,
            result_json_url VARCHAR(255) NOT NULL,
            created_at VARCHAR(40) NOT NULL,
            PRIMARY KEY (id),
            CONSTRAINT fk_detection_logs_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
    """)
    _ensure_migration_columns(conn)


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (table_name, column_name),
    )
    return bool(cursor.fetchone())


def _ensure_column(conn, table_name: str, column_name: str, sql_fragment: str):
    if not _column_exists(conn, table_name, column_name):
        db_execute(conn, f"ALTER TABLE {table_name} ADD COLUMN {sql_fragment}")


def _ensure_migration_columns(conn):
    _ensure_column(conn, "users", "salt", "salt VARCHAR(64) NOT NULL DEFAULT '' AFTER password")
    _ensure_column(conn, "users", "updated_at", "updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at")
    _ensure_column(conn, "users", "status", "status TINYINT NOT NULL DEFAULT 1 AFTER role")


def init_db():
    with get_db() as conn:
        _ensure_schema(conn)
