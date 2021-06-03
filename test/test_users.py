from fastapi.testclient import TestClient
import pytest
import requests

from rocketleague_spotify import app
from rocketleague_spotify.settings import settings

if settings().test_url:
    base_url = settings().test_url
else:
    base_url = ""


user1 = {"id": "abcd1234", "goal_music_uri": "asdfasdf12341234", "access_token": "poiu0987"}
user2 = {"id": "zxcv5768", "goal_music_uri": "zxcvzxcv56785678", "access_token": "mnvb4321"}
users = (user1, user2)


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
    for user in users:
        res = client.delete(f"{base_url}/users/{user['id']}", params={"access_token": user["access_token"]})
        assert res.status_code in [404, 200]


class TestEdgeCases:
    def test_empty(self, client):
        res = client.get(f"{base_url}/users/")
        assert res.status_code == 200
        assert len(res.json()) == 0

        res = client.get(f"{base_url}/users/does_not_exist")
        assert res.status_code == 404

        res = client.delete(f"{base_url}/user/does_not_exist")
        assert res.status_code == 404


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

        res = client.delete(f"{base_url}/users/{user1['id']}", params={"access_token": user1["access_token"]})
        assert res.status_code == 200

    def test_multiple_users(self, client, handle_test_users):
        res = client.put(f"{base_url}/users/", json=user1)
        assert res.status_code == 201
        res = client.put(f"{base_url}/users/", json=user2)
        assert res.status_code == 201

        res = client.get(f"{base_url}/users/", params={"user_ids": [user1["id"], user2["id"]]})
        res2 = client.get(f"{base_url}/users/", params={"user_ids": ",".join([user1["id"], user2["id"]])})
        assert res.text == res2.text
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

        res = client.delete(f"{base_url}/users/{user1['id']}", params={"access_token": user1["access_token"]})
        assert res.status_code == 200
        res = client.delete(f"{base_url}/users/{user2['id']}", params={"access_token": user2["access_token"]})
        assert res.status_code == 200

        res = client.get(f"{base_url}/users/", params={"user_ids": [user1["id"], user2["id"]]})
        assert res.status_code == 200
        assert len(res.json()) == 0


class TestAuth:
    def test_create_update_user(self, client, handle_test_users):
        res = client.put(f"{base_url}/users/", json=user1)
        assert res.status_code == 201

        user1_no_token = user1.copy()
        user1_no_token["access_token"] = "wrong"
        user1_no_token["goal_music_uri"] = "new"
        res = client.put(f"{base_url}/users/", json=user1_no_token)
        assert res.status_code == 403

        res = client.get(f"{base_url}/users/{user1['id']}")
        assert res.status_code == 200
        assert res.json()["goal_music_uri"] == user1["goal_music_uri"]

    def test_delete_user(self, client, handle_test_users):
        res = client.put(f"{base_url}/users/", json=user1)
        assert res.status_code == 201

        res = client.delete(f"{base_url}/users/{user1['id']}", params={"access_token": "1234asdf"})
        assert res.status_code == 403

        res = client.get(f"{base_url}/users/{user1['id']}")
        assert res.status_code == 200
        assert res.json()["goal_music_uri"] == user1["goal_music_uri"]

    def test_no_leaked_tokens(self, client, handle_test_users):
        res = client.put(f"{base_url}/users/", json=user1)
        assert res.status_code == 201
        res = client.put(f"{base_url}/users/", json=user2)
        assert res.status_code == 201

        for user in users:
            res = client.get(f"{base_url}/users/{user['id']}")
            assert res.status_code == 200
            assert res.json().get("access_token") is None

        res = client.get(f"{base_url}/users", params={"user_ids": [user1["id"], user2["id"]]})
        assert res.status_code == 200
        json_res = res.json()
        assert json_res[0].get("access_token") is None and json_res[1].get("access_token") is None
