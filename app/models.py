from datetime import datetime

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
    expires_at: datetime
    created_at: datetime


class MetricSample(SQLModel, table=True):
    """一次服务器指标采样，构成前端图表的时间序列。"""

    id: int | None = Field(default=None, primary_key=True)
    ts: datetime
    cpu_percent: float
    mem_percent: float
    disk_percent: float
    net_rx_bytes: int
    net_tx_bytes: int
    uptime_seconds: int
    load1: float | None = None
