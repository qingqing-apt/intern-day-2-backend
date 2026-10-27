# intern-day-2-backend

实习生第二天练习 · 后端服务：FastAPI 登录鉴权 + 服务器指标采集 API（类 Prometheus + node_exporter 的最小实现）。

## 功能范围

- 账号密码登录（真实后端校验，禁止纯前端模拟）
- 获取当前用户、退出登录（服务端删除会话）
- 服务器指标采集：CPU / 内存 / 磁盘 / 网络收发 / 系统运行时长，每 5 秒采样一次并存入 SQLite
- 指标查询：`latest` / `history` / `summary` / 手动 `collect`，**全部要求登录**

自选功能主题：**服务器监控台**。登录后的仪表盘数据全部来自本仓库的采集接口。

## 接口约定

| 方法 | 路径 | 说明 | 鉴权 |
| --- | --- | --- | --- |
| GET | `/health` | 健康检查 | 否 |
| POST | `/auth/login` | 账号密码登录，返回不透明令牌 | 否 |
| GET | `/auth/me` | 当前用户信息 | 是 |
| POST | `/auth/logout` | 退出登录，删除服务端会话 | 是 |
| GET | `/metrics/latest` | 最新一条采样 | 是 |
| GET | `/metrics/history?minutes=10` | 最近 N 分钟采样（1–1440） | 是 |
| GET | `/metrics/summary` | 主机信息 + 采样统计 + 最新值 | 是 |
| POST | `/metrics/collect` | 手动触发一次采集 | 是 |

请求头统一为 `Authorization: Bearer <token>`。接口文档启动后见 `/docs`。

## 开发环境进入方式

本仓库开发容器基于第一天的 `git-base:1.1` 镜像构建（已内置 git 2.34.1 与团队 GitHub 只读密钥），在上层追加 uv 与 Python 3.12。

前置条件：

1. 本机已导入基础镜像：`docker load -i git-base-1.1.tar.gz`
2. VS Code 已安装 Dev Containers 扩展
3. 在容器内配置自己的 git 身份与推送密钥（基础镜像内置的密钥只读，不能 push）：

```bash
git config --global user.name  "你的名字"
git config --global user.email "你的邮箱"
ssh-keygen -t ed25519   # 公钥添加到个人 GitHub 账号
```

操作：VS Code 打开本仓库目录 → 命令面板 → `Dev Containers: Reopen in Container`。容器创建后会自动执行 `uv sync --frozen`。

> 注意：本仓库尚未提交 `uv.lock`，首次进入容器后先执行一次 `uv lock` 生成锁文件再 `uv sync`（锁文件需提交进仓库，CI 与镜像构建都依赖它）。

## 独立启动命令

在本仓库根目录执行：

```bash
docker compose up --build -d
docker compose ps
docker compose logs --tail=100
```

服务监听 `0.0.0.0:8000`，映射到宿主机 `8000`。停止并重新创建：`docker compose down && docker compose up --build -d`。

本地开发（不进 compose）也可以在容器内直接 `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`。

## 配套仓库与联调版本

- 配套前端仓库：https://github.com/qingqing-apt/intern-day-2-frontend
- 联调方式：**浏览器直连宿主机端口**（前端 5173 / 后端 8000），两个 Compose 项目互相独立，不共享服务发现
- 前端通过环境变量 `VITE_API_BASE_URL=http://localhost:8000` 指向本服务
- CORS 已放行 `http://localhost:5173`（`ALLOWED_ORIGINS` 可改）
- 实际联调使用的双方分支/提交版本：后端 `feat/login-and-custom-feature`（`1806934`）× 前端同分支（`7b4f039`）

## 访问地址

- 接口文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 练习账号初始化方法

无需注册。服务首次启动时自动用环境变量创建练习账号（`.env.example` 中有占位值）：

- 账号：`intern`
- 密码：`intern-pass-123`

均为虚构数据。可通过 `SEED_USERNAME` / `SEED_PASSWORD` 环境变量覆盖。

## 登录状态方案

随机不透明令牌（`secrets.token_urlsafe(32)`）+ 服务端会话表：

- 登录成功签发令牌，有效期 `SESSION_TTL_MINUTES`（默认 60 分钟）
- 令牌存 `SessionToken` 表，含过期时间；退出登录即删除记录
- 未携带、伪造、过期、已退出的令牌访问受保护接口一律返回 `401`
- 前端将令牌保存在浏览器本地，请求自动携带 `Authorization: Bearer` 头；401 时前端清理本地状态并提示重新登录
- 刷新页面：前端重新调用 `/auth/me` 向后端校验，不依赖前端标志

## 数据保存方式

- SQLite（默认容器内 `/data/app.db`，挂载 `./data` 卷；本地开发为 `./data/app.db`）
- 用户与会话表：账号重启后保留；**会话过期时间自然生效**
- 指标采样：仅保留最近 `METRICS_RETENTION` 条（默认 720 条 ≈ 1 小时），更早的自动清理
- 重启服务后指标历史从零开始累积，账号可继续使用

## 自测记录

联调环境：2026-10-27，后端 `feat/login-and-custom-feature`（`1806934`）× 前端同分支（`7b4f039`），容器部署在 10.0.11.100。

| 场景 | 命令/操作 | 结果 |
|---|---|---|
| 正常登录 | `POST /auth/login` 正确凭证 | 200，返回 `token` 与 `expires_in: 3600` |
| 错误密码 | `POST /auth/login` 错误密码 | 401，`{"detail":"账号或密码错误"}` |
| 空字段 | 提交空 username/password | 422，字段校验拦截 |
| 未携带凭证 | `GET /metrics/latest` 无 Authorization | 401 |
| 伪造凭证 | 携带 `Authorization: Bearer fake` | 401 |
| 凭证过期 | `SESSION_TTL_MINUTES=1` 启动，登录后等待 65 秒 | 过期前 200，过期后 401 |
| 退出登录 | `POST /auth/logout` 后用旧令牌访问 | 204 登出成功；旧令牌访问返回 401 |
| 容器 restart | `docker restart` | 账号与指标数据保留（容器文件系统未变） |
| 容器重建 | `docker rm` + `docker run` | 新库：账号由种子数据重建，指标从 1 条重新累积，旧令牌 401 |
| 采集器工作 | `GET /metrics/summary` | 返回真实采样（CPU/内存/磁盘/网络/运行时长/负载） |

```bash
# 快速验证示例
TOKEN=$(curl -s -X POST localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"intern","password":"intern-pass-123"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -s localhost:8000/auth/me -H "Authorization: Bearer $TOKEN"
curl -s localhost:8000/auth/me                       # 预期 401
curl -s -X POST localhost:8000/metrics/collect -H "Authorization: Bearer $TOKEN"
```

```bash
# 快速验证示例
TOKEN=$(curl -s -X POST localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"intern","password":"intern-pass-123"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -s localhost:8000/auth/me -H "Authorization: Bearer $TOKEN"
curl -s localhost:8000/auth/me                       # 预期 401
curl -s -X POST localhost:8000/metrics/collect -H "Authorization: Bearer $TOKEN"
```

## 已知问题与限制

- 采集的是**容器所在运行时环境**的指标（Docker Desktop 场景即 Linux 虚拟机），不是 Windows 宿主机本身
- `load1` 在非 Linux 平台为 `null`
- 单 worker 单实例设计，未做多实例去重；重启后历史清空（见上）
- 练习项目：无注册、无找回密码、无角色权限
