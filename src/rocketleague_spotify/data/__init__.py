import motor.motor_asyncio

from rocketleague_spotify.settings import settings


_client = motor.motor_asyncio.AsyncIOMotorClient(settings().mongo_url)
db = _client.rls_db
