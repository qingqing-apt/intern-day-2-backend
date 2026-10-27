import asyncio
import platform
import socket

import psutil
from sqlmodel import Session, delete, func, select

from .config import settings
from .db import engine
from .models import MetricSample
from .timeutil import utcnow


def _prime_cpu() -> None:
    """cpu_percent(interval=None) 需要一次前置调用才能给出差值。"""
    try:
        psutil.cpu_percent(interval=None)
    except Exception:
        pass


def collect_sample(db: Session) -> MetricSample:
    """采集一次服务器指标并入库。"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    try:
        load1: float | None = psutil.getloadavg()[0]
    except (AttributeError, OSError):
        load1 = None  # 非 Linux 平台没有 load average
    sample = MetricSample(
        ts=utcnow(),
        cpu_percent=round(psutil.cpu_percent(interval=None), 2),
        mem_percent=round(memory.percent, 2),
        disk_percent=round(disk.percent, 2),
        net_rx_bytes=net.bytes_recv if net else 0,
        net_tx_bytes=net.bytes_sent if net else 0,
        uptime_seconds=int(utcnow().timestamp() - psutil.boot_time()),
        load1=load1,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


def trim_samples(db: Session) -> None:
    """只保留最近 N 条样本，避免 SQLite 无限增长。"""
    max_id = db.exec(select(func.max(MetricSample.id))).one()
    if max_id is not None and max_id > settings.metrics_retention:
        db.exec(delete(MetricSample).where(MetricSample.id <= max_id - settings.metrics_retention))
        db.commit()


async def collector_loop() -> None:
    _prime_cpu()
    while True:
        try:
            with Session(engine) as db:
                collect_sample(db)
                trim_samples(db)
        except Exception:
            pass  # 单次采集失败不影响服务继续运行
        await asyncio.sleep(settings.collect_interval_seconds)


def host_info() -> dict:
    return {"hostname": socket.gethostname(), "platform": platform.platform()}
