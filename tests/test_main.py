def test_root_endpoint(test_client):
    """Тест корневого эндпоинта"""
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Добро пожаловать" in data["message"]


def test_health_check(test_client):
    """Тест health check"""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "operational"
