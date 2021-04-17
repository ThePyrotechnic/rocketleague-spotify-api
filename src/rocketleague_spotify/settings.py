from functools import lru_cache
import importlib.resources
import os
from typing import Optional

from pydantic import BaseSettings, AnyUrl


with importlib.resources.path("rocketleague_spotify", ".env") as env_file:
    env_filepath = str(env_file.resolve().absolute())


@lru_cache
def settings():
    return _Settings()


class _Settings(BaseSettings):
    mongo_url: AnyUrl
    test_url: Optional[AnyUrl]

    class Config:
        if os.environ.get("NO_ENV_FILE") != "true":
            env_file = env_filepath
            env_file_encoding = 'utf-8'
