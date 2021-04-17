from fastapi.testclient import TestClient
import pytest

from rocketleague_spotify import app

client = TestClient(app)


user1 = {"id": "abcd1234", "goal_music_uri": "asdfasdf12341234"}
user2 = {"id": "zxcv5768", "goal_music_uri": "zxcvzxcv56785678"}


@pytest.fixture
def handle_test_users():  # Ensure users are deleted before the test runs
    client.delete("/users/", params={"user_ids": [user1["id"], user2["id"]]})


class TestUsers:
    def test_user(self, handle_test_users):
        res = client.put("/users/", json=user1)
        assert res.status_code == 201

        res = client.put("/users/", json=user1)
        assert res.status_code == 200

        user1["goal_music_uri"] = "qwerqwer67896789"
        res = client.put("/users/", json=user1)
        assert res.status_code == 200

        res = client.get(f"/users/{user1['id']}")
        assert res.status_code == 200
        json_user = res.json()
        assert json_user["id"] == user1["id"]
        assert json_user["goal_music_uri"] == user1["goal_music_uri"]

        res = client.delete(f"/users/{user1['id']}")
        assert res.status_code == 200

    def test_multiple_users(self, handle_test_users):
        res = client.put("/users/", json=user1)
        assert res.status_code == 201
        res = client.put("/users/", json=user2)
        assert res.status_code == 201

        res = client.get("/users/", params={"user_ids": [user1["id"], user2["id"]]})
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

        res = client.delete("/users/", params={"user_ids": [user1["id"], user2["id"]]})
        assert res.status_code == 200
        assert res.json()["deleted_count"] == 2

        res = client.get("/users/", params={"user_ids": [user1["id"], user2["id"]]})
        assert res.status_code == 404
