from fastapi.testclient import TestClient
import pytest
import requests

from rocketleague_spotify import app
from rocketleague_spotify.settings import settings

if settings().test_url:
    base_url = settings().test_url
else:
    base_url = ""


user1 = {"id": "abcd1234", "goal_music_uri": "asdfasdf12341234"}
user2 = {"id": "zxcv5768", "goal_music_uri": "zxcvzxcv56785678"}


@pytest.fixture
def client():
    if settings().test_url:
        with requests.session() as c:
            yield c
    else:
        with TestClient(app) as c:
            yield c


@pytest.fixture
def handle_test_users(client):  # Ensure users are deleted before the test runs
    client.delete(f"{base_url}/users/", params={"user_ids": [user1["id"], user2["id"]]})


class TestUsers:
    def test_user(self, client, handle_test_users):
        res = client.put(f"{base_url}/users/", json=user1)
        assert res.status_code == 201

        res = client.put(f"{base_url}/users/", json=user1)
        assert res.status_code == 200

        user1["goal_music_uri"] = "qwerqwer67896789"
        res = client.put(f"{base_url}/users/", json=user1)
        assert res.status_code == 200

        res = client.get(f"{base_url}/users/{user1['id']}")
        assert res.status_code == 200
        json_user = res.json()
        assert json_user["id"] == user1["id"]
        assert json_user["goal_music_uri"] == user1["goal_music_uri"]

        res = client.delete(f"{base_url}/users/{user1['id']}")
        assert res.status_code == 200

    def test_multiple_users(self, client, handle_test_users):
        res = client.put(f"{base_url}/users/", json=user1)
        assert res.status_code == 201
        res = client.put(f"{base_url}/users/", json=user2)
        assert res.status_code == 201

        res = client.get(f"{base_url}/users/", params={"user_ids": [user1["id"], user2["id"]]})
        assert res.status_code == 200
        json_res = res.json()
        assert len(json_res) == 2
        if json_res[0]["id"] == user1["id"]:
            json_user1 = json_res[0]
            json_user2 = json_res[1]
        else:
            json_user1 = json_res[1]
            json_user2 = json_res[0]
        assert json_user1["id"] == user1["id"] and json_user2["id"] == user2["id"]
        assert json_user1["goal_music_uri"] == user1["goal_music_uri"] and json_user2["goal_music_uri"] == user2["goal_music_uri"]

        res = client.delete(f"{base_url}/users/", params={"user_ids": [user1["id"], user2["id"]]})
        assert res.status_code == 200
        assert res.json()["deleted_count"] == 2

        res = client.get(f"{base_url}/users/", params={"user_ids": [user1["id"], user2["id"]]})
        assert res.status_code == 404
