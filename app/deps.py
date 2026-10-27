from fastapi import Depends, Header, HTTPException
from sqlmodel import Session, select

from .db import get_session
from .models import SessionToken, User
from .timeutil import utcnow


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_session),
) -> User:
    """受保护接口的统一鉴权依赖：未携带、伪造、过期、已退出的令牌一律 401。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或凭证无效")
    token = authorization.removeprefix("Bearer ").strip()
    record = db.exec(select(SessionToken).where(SessionToken.token == token)).first()
    if record is None or record.expires_at <= utcnow():
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    user = db.get(User, record.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
