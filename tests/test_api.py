from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


VALID_FLOW = {
    "duration": 12.4,
    "protocol": "tcp",
    "source_port": "0x1F90",
    "direction": "->",
    "destination_port": 443,
    "connection_state": "S",
    "source_tos": 0,
    "destination_tos": 0,
    "total_packets": 15,
    "total_bytes": 1820,
    "source_bytes": 940,
}


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "BotSentinel API"
    assert data["status"] == "online"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["model"] == "loaded"


def test_predict_valid_flow():
    response = client.post("/predict", json=VALID_FLOW)

    assert response.status_code == 200

    data = response.json()

    assert data["prediction"] in {"Botnet", "Non-Botnet"}
    assert isinstance(data["is_botnet"], bool)
    assert 0 <= data["botnet_probability"] <= 1
    assert 0 <= data["confidence"] <= 1


def test_predict_rejects_negative_duration():
    invalid_flow = {
        **VALID_FLOW,
        "duration": -12.4,
    }

    response = client.post("/predict", json=invalid_flow)

    assert response.status_code == 422


def test_predict_rejects_negative_packet_count():
    invalid_flow = {
        **VALID_FLOW,
        "total_packets": -1,
    }

    response = client.post("/predict", json=invalid_flow)

    assert response.status_code == 422


def test_predict_rejects_invalid_json_types():
    invalid_flow = {
        **VALID_FLOW,
        "duration": "not-a-number",
    }

    response = client.post("/predict", json=invalid_flow)

    assert response.status_code == 422


def test_predict_handles_hexadecimal_source_port():
    response = client.post("/predict", json=VALID_FLOW)

    assert response.status_code == 200


def test_cors_headers():
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    response = client.options(
        "/predict",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"