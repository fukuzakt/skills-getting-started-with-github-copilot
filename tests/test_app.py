import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Arrange-Act-Assert pattern

def test_get_activities():
    # Arrange: 何も登録されていない状態
    # Act: GETリクエスト
    response = client.get("/activities")
    # Assert: ステータスと内容
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_signup_and_duplicate():
    # Arrange: テスト用データ
    activity = list(client.get("/activities").json().keys())[0]
    email = "testuser@mergington.edu"
    # Act: 初回登録
    response1 = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert: 成功
    assert response1.status_code == 200
    # Act: 重複登録
    response2 = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert: エラー
    assert response2.status_code == 400
    assert "既に登録されています" in response2.json()["detail"]


def test_signup_full():
    # Arrange: 定員1の活動を仮定
    activity = None
    for name, details in client.get("/activities").json().items():
        if details["max_participants"] == 1:
            activity = name
            break
    if not activity:
        pytest.skip("定員1の活動がないためスキップ")
    email1 = "user1@mergington.edu"
    email2 = "user2@mergington.edu"
    # Act: 1人目登録
    response1 = client.post(f"/activities/{activity}/signup?email={email1}")
    # Assert: 成功
    assert response1.status_code == 200
    # Act: 2人目登録
    response2 = client.post(f"/activities/{activity}/signup?email={email2}")
    # Assert: 定員超過
    assert response2.status_code == 400
    assert "Activity is full" in response2.json()["detail"]


def test_unregister():
    # Arrange: 登録済みユーザー
    activity = list(client.get("/activities").json().keys())[0]
    email = "deleteuser@mergington.edu"
    client.post(f"/activities/{activity}/signup?email={email}")
    # Act: DELETEリクエスト
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert: 成功
    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]
