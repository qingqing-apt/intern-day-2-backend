from datetime import timedelta

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, func, select

from ..collector import collect_sample, host_info
from ..config import settings
from ..db import get_session
from ..deps import get_current_user
from ..models import MetricSample, User
from ..schemas import MetricSampleOut, SummaryOut
from ..timeutil import utcnow

router = APIRouter()


@router.get("/latest", response_model=MetricSampleOut | None)
def latest(db: Session = Depends(get_session), _: User = Depends(get_current_user)):
    return db.exec(select(MetricSample).order_by(MetricSample.ts.desc()).limit(1)).first()


@router.get("/history", response_model=list[MetricSampleOut])
def history(
    minutes: int = Query(default=10, ge=1, le=1440),
    db: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    since = utcnow() - timedelta(minutes=minutes)
    rows = db.exec(
        select(MetricSample).where(MetricSample.ts >= since).order_by(MetricSample.ts.asc())
    ).all()
    return rows


@router.get("/summary", response_model=SummaryOut)
def summary(db: Session = Depends(get_session), _: User = Depends(get_current_user)):
    latest_row = db.exec(select(MetricSample).order_by(MetricSample.ts.desc()).limit(1)).first()
    total = db.exec(select(func.count()).select_from(MetricSample)).one()
    info = host_info()
    return SummaryOut(
        hostname=info["hostname"],
        platform=info["platform"],
        collect_interval_seconds=settings.collect_interval_seconds,
        total_samples=total,
        # Pydantic v2 不会自动把 ORM 对象转成嵌套模型，这里显式转换
        latest=MetricSampleOut.model_validate(latest_row) if latest_row else None,
    )


@router.post("/collect", response_model=MetricSampleOut)
def collect_now(db: Session = Depends(get_session), _: User = Depends(get_current_user)):
    """手动触发一次采集，演示时不用等下一个采样周期。"""
    return collect_sample(db)
