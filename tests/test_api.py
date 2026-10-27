import os
import tempfile
from pathlib import Path

# 必须在导入 app 之前设置，保证测试使用独立临时数据库
os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.mkdtemp()).as_posix()}/test.db"
os.environ["COLLECT_INTERVAL_SECONDS"] = "9999"
os.environ["SEED_USERNAME"] = "tester"
os.environ["SEED_PASSWORD"] = "test-pass-123"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _login() -> str:
    resp = client.post("/auth/login", json={"username": "tester", "password": "test-pass-123"})
    assert resp.status_code == 200
    return resp.json()["token"]


def test_health():
    assert client.get("/health").status_code == 200


def test_login_me_logout_flow():
    token = _login()

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "tester"

    # 未携带凭证
    assert client.get("/auth/me").status_code == 401
    # 错误密码
    wrong = client.post("/auth/login", json={"username": "tester", "password": "wrong-pass"})
    assert wrong.status_code == 401
    # 不存在的账号
    missing = client.post("/auth/login", json={"username": "nobody", "password": "whatever1"})
    assert missing.status_code == 401

    # 退出后旧令牌失效
    client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_metrics_requires_login():
    assert client.get("/metrics/latest").status_code == 401
    assert client.get("/metrics/history").status_code == 401
    assert client.get("/metrics/summary").status_code == 401

    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    collected = client.post("/metrics/collect", headers=headers)
    assert collected.status_code == 200
    assert "cpu_percent" in collected.json()

    assert client.get("/metrics/latest", headers=headers).status_code == 200
    history = client.get("/metrics/history?minutes=10", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) >= 1
