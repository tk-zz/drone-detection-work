import os
from functools import lru_cache
from pathlib import Path

from backend.core.constants import BASE_DIR


def _strip_wrapping_quotes(value: str):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _load_env_file(env_path: Path):
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = _strip_wrapping_quotes(value.strip())
        os.environ[key] = value


@lru_cache(maxsize=1)
def load_local_env():
    project_dir = BASE_DIR.parent
    for env_path in (
        project_dir / ".env",
        project_dir / ".env.local",
        BASE_DIR / ".env",
        BASE_DIR / ".env.local",
    ):
        _load_env_file(env_path)


def get_mysql_config():
    load_local_env()
    try:
        import pymysql.cursors
    except ImportError as exc:
        raise RuntimeError("使用 MySQL 需要先安装 pymysql：pip install pymysql") from exc

    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "drone-detection-sql"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False,
    }
