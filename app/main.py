import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .collector import collector_loop
from .config import settings
from .db import init_db
from .routers import auth, metrics
from .seed import seed_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_user()
    task = asyncio.create_task(collector_loop())
    yield
    task.cancel()


app = FastAPI(title="intern-day-2-backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])


@app.get("/health")
def health():
    return {"status": "ok"}
