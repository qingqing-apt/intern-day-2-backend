FROM python:3.12-slim

# 开发容器所需的基础工具：git 用于版本操作，ssh 用于访问私有仓库
RUN apt-get update \
    && apt-get install -y --no-install-recommends git openssh-client ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# 与运行时镜像同源引入 uv，保证开发与运行使用同一套依赖解析
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workspace
