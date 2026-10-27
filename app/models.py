from datetime import datetime

from sqlalchemy import Column, DateTime as SADateTime
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str


class SessionToken(SQLModel, table=True):
    """不透明会话令牌：退出登录即删除记录，旧令牌立即失效。"""

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(index=True, unique=True)
    user_id: int = Field(foreign_key="user.id")
    # 约定：全部使用 naive UTC 存储，展示时由前端按本地时区转换。
    # SQLModel 0.0.48 默认把 datetime 映射为 UTCDateTime（要求带时区），
    # 这里显式使用 SQLAlchemy DateTime 以保留 naive UTC 约定。
    expires_at: datetime = Field(sa_column=Column(SADateTime, nullable=False))
    created_at: datetime = Field(sa_column=Column(SADateTime, nullable=False))


class MetricSample(SQLModel, table=True):
    """一次服务器指标采样，构成前端图表的时间序列。"""

    id: int | None = Field(default=None, primary_key=True)
    ts: datetime = Field(sa_column=Column(SADateTime, nullable=False))
    cpu_percent: float
    mem_percent: float
    disk_percent: float
    net_rx_bytes: int
    net_tx_bytes: int
    uptime_seconds: int
    load1: float | None = None
