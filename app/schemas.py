from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic import Field as PydanticField


class LoginIn(BaseModel):
    username: str = PydanticField(min_length=1, max_length=64)
    password: str = PydanticField(min_length=1, max_length=128)


class TokenOut(BaseModel):
    token: str
    expires_in: int


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 允许直接转换 ORM 对象

    id: int
    username: str


class MetricSampleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ts: datetime
    cpu_percent: float
    mem_percent: float
    disk_percent: float
    net_rx_bytes: int
    net_tx_bytes: int
    uptime_seconds: int
    load1: float | None = None


class SummaryOut(BaseModel):
    hostname: str
    platform: str
    collect_interval_seconds: float
    total_samples: int
    latest: MetricSampleOut | None = None
