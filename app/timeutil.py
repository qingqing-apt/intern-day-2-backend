from datetime import UTC, datetime


def utcnow() -> datetime:
    """统一返回 naive UTC 时间，避免 SQLite 时区比较报错。"""
    return datetime.now(UTC).replace(tzinfo=None)
