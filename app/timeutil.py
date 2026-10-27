from datetime import datetime, timezone


def utcnow() -> datetime:
    """统一返回 naive UTC 时间，避免 SQLite 时区比较报错。"""
    return datetime.now(timezone.utc).replace(tzinfo=None)
