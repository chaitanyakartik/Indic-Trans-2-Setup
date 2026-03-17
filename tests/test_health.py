import requests

BASE_URL = "http://localhost:8003"


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["models_loaded"] is True
