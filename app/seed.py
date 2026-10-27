from sqlmodel import Session, select

from .config import settings
from .db import engine
from .models import User
from .security import hash_password


def seed_user() -> None:
    """用环境变量里的虚构账号初始化练习账号，重复执行不会覆盖。"""
    with Session(engine) as db:
        exists = db.exec(select(User).where(User.username == settings.seed_username)).first()
        if exists is None:
            db.add(
                User(
                    username=settings.seed_username,
                    password_hash=hash_password(settings.seed_password),
                )
            )
            db.commit()
