import motor.motor_asyncio
from motor .motor_asyncio import AsyncIOMotorClient

from rocketleague_spotify.settings import settings


_client: AsyncIOMotorClient = None


def get_db():
    return _client.rls_db


async def connect_db():
    global _client
    _client = motor.motor_asyncio.AsyncIOMotorClient(settings().mongo_url)


async def close_db():
    _client.close()
