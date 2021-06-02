from typing import List

from fastapi import FastAPI, status, Query, Response
from pymongo.results import UpdateResult
import uvicorn

from rocketleague_spotify.data import get_db, connect_db, close_db
from rocketleague_spotify.models import User, UserWithAccessToken, UpdateUserModel

app = FastAPI(
    title="Rocket League + Spotify Backend API",
    description="",
    version="1.0.0"
)

app.add_event_handler("startup", connect_db)
app.add_event_handler("shutdown", close_db)


@app.put("/users/", tags=["Users"])
async def create_or_update_user(user_data: UserWithAccessToken, response: Response):
    """Update an existing user or create a new one if no user with the given ID is found"""
    res = await get_db().users.find_one({"id": user_data.id})
    if res is not None:
        user: UserWithAccessToken = UserWithAccessToken.parse_obj(res)
        if user_data.access_token != user.access_token:  # Bad access token
            response.status_code = status.HTTP_403_FORBIDDEN

    if response.status_code is None:  # Only update user if current return status hasn't been set
        res: UpdateResult = await get_db().users.update_one({"id": user_data.id}, {"$set": user_data.dict()}, upsert=True)
        if res.upserted_id:  # Presence of this variable indicates that a new object was created
            response.status_code = status.HTTP_201_CREATED
        elif res.matched_count == 0:  # indicates nothing was found
            response.status_code = status.HTTP_404_NOT_FOUND
        # else the return code will be 200


@app.patch("/users/{user_id}", tags=["Users"])
async def update_user(user_id: str, user_data: UpdateUserModel, response: Response):
    """Update an existing user. If an ID is passed in the JSON body, it is ignored"""
    res = await get_db().users.find_one({"id": user_data.id})
    if res is not None:
        user: UserWithAccessToken = UserWithAccessToken.parse_obj(res)
        if user_data.access_token != user.access_token:  # Bad access token
            response.status_code = status.HTTP_403_FORBIDDEN
        else:
            res: UpdateResult = await get_db().users.update_one({"id": user_id}, {"$set": user_data.dict(exclude={"id"})})
            if res.modified_count != 1:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        response.status_code = status.HTTP_404_NOT_FOUND


@app.get("/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: str, response: Response):
    """Get a single user by ID"""
    res = await get_db().users.find_one({"id": user_id})
    if res is None:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        return User.parse_obj(res)


@app.get("/users/", response_model=List[User], tags=["Users"])
async def get_users(user_ids: List[str] = Query(None)):
    """
    Get a list of users. If a user is not found it will not be returned.
    If no users are found the response will be an empty list
    """
    if not user_ids:
        user_ids = []

    if len(user_ids) == 1:
        user_ids = user_ids[0].split(",")  # Also accept a comma-separated list

    cursor = get_db().users.find({"id": {"$in": user_ids}})
    res = await cursor.to_list(length=len(user_ids))
    if len(res) == 0:
        return []
    else:
        return res


@app.delete("/users/{user_id}", tags=["Users"])
async def delete_user(response: Response, user_id: str, access_token: str = Query(None)):
    """Delete a single user by ID"""
    res = await get_db().users.find_one({"id": user_id})
    if res is not None:
        user: UserWithAccessToken = UserWithAccessToken.parse_obj(res)
        if access_token != user.access_token:  # Bad access token
            response.status_code = status.HTTP_403_FORBIDDEN
        else:
            res = await get_db().users.delete_one({"id": user_id})
            if res.deleted_count != 1:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        response.status_code = status.HTTP_404_NOT_FOUND


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
