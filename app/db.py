import os

from sqlmodel import Session, SQLModel, create_engine

from .config import settings


def _ensure_sqlite_dir(url: str) -> None:
    """为 SQLite 文件提前创建目录（本地开发相对路径 /data 的情况）。"""
    if not url.startswith("sqlite:///"):
        return
    path = url[len("sqlite:///") :]
    if not path or path == ":memory:":
        return
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


_ensure_sqlite_dir(settings.database_url)

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=_connect_args)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
