FROM git-base:1.1

# 在第一天的基础镜像上追加 uv，并由 uv 管理 Python 3.12
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && uv python install 3.12 \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:${PATH}"
