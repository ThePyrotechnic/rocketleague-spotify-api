from typing import List

from fastapi import FastAPI, status, Query, Response
from pymongo.results import UpdateResult
import uvicorn

from rocketleague_spotify.data import get_db, connect_db, close_db
from rocketleague_spotify.models import User, UpdateUserModel, DeleteManyResponse

app = FastAPI(
    title="Rocket League + Spotify Backend API",
    description="",
    version="0.0.0",
    docs_url=None
)

app.add_event_handler("startup", connect_db)
app.add_event_handler("shutdown", close_db)


@app.put("/users/", tags=["Users"])
async def create_or_update_user(user_data: User, response: Response):
    """Update an existing user or create a new one if no user with the given ID is found"""
    res: UpdateResult = await get_db().users.update_one({"id": user_data.id}, {"$set": user_data.dict()}, upsert=True)

    if res.upserted_id:  # Presence of this variable indicates that a new object was created
        response.status_code = status.HTTP_201_CREATED
    elif res.matched_count == 0:  # indicates nothing was found
        response.status_code = status.HTTP_404_NOT_FOUND


@app.patch("/users/{user_id}", tags=["Users"])
async def update_user(user_id: str, user_data: UpdateUserModel, response: Response):
    """Update an existing user. If an ID is passed in the JSON body, it is ignored"""
    res: UpdateResult = await get_db().users.update_one({"id": user_id}, {"$set": user_data.dict(exclude={"id"})})

    if res.modified_count != 1:
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
async def get_users(response: Response, user_ids: List[str] = Query(None)):
    """
    Get a list of users. If a user is not found it will not be returned.
    If no users are found the response code will be 404
    """
    cursor = get_db().users.find({"id": {"$in": user_ids}})
    res = await cursor.to_list(length=len(user_ids))
    if len(res) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        return res


@app.delete("/users/{user_id}", tags=["Users"])
async def delete_user(response: Response, user_id: str):
    """Delete a single user by ID"""
    res = await get_db().users.delete_one({"id": user_id})
    if res.deleted_count != 1:
        response.status_code = status.HTTP_404_NOT_FOUND


@app.delete("/users/", response_model=DeleteManyResponse, tags=["Users"])
async def delete_users(response: Response, user_ids: List[str] = Query(None)):
    """Delete multiple users. If no users are deleted the response code will be 404"""
    res = await get_db().users.delete_many({"id": {"$in": user_ids}})
    if res.deleted_count < 1:
        response.status_code = status.HTTP_404_NOT_FOUND
    return {"deleted_count": res.deleted_count}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
