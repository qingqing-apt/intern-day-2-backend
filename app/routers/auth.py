from datetime import timedelta

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlmodel import Session, select

from ..config import settings
from ..db import get_session
from ..deps import get_current_user
from ..models import SessionToken, User
from ..schemas import LoginIn, TokenOut, UserOut
from ..security import new_token, verify_password
from ..timeutil import utcnow

router = APIRouter()


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == data.username)).first()
    # 账号不存在与密码错误返回同一条提示，不泄露账号是否存在
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    token = new_token()
    db.add(
        SessionToken(
            token=token,
            user_id=user.id,
            expires_at=utcnow() + timedelta(minutes=settings.session_ttl_minutes),
            created_at=utcnow(),
        )
    )
    db.commit()
    return TokenOut(token=token, expires_in=settings.session_ttl_minutes * 60)


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current


@router.post("/logout")
def logout(authorization: str | None = Header(default=None), db: Session = Depends(get_session)):
    """服务端删除会话，退出后旧令牌立即失效。"""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        record = db.exec(select(SessionToken).where(SessionToken.token == token)).first()
        if record is not None:
            db.delete(record)
            db.commit()
    return {"ok": True}
