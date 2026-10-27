FROM python:3.12-slim

WORKDIR /app

# 按锁文件安装依赖，不带入开发依赖
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock ./
COPY app ./app
RUN uv sync --frozen --no-dev

# 容器内监听 0.0.0.0，SQLite 数据写入 /data 卷
ENV DATABASE_URL=sqlite:////data/app.db
RUN mkdir -p /data

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
