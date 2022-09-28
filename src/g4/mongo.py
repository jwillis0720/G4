# pyright: reportMissingTypeStubs=true
import logging
import os
from pathlib import Path
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from g4.config import Settings

logger = logging.getLogger("Mongo")


# write authentication error class
class AuthenticationError(Exception):
    def __init__(self, exception_str: str) -> None:
        self.exception_str = exception_str

    def __str__(self) -> str:
        return self.exception_str


class Mongo:
    def __init__(self, settings: Settings, use_async: bool = True) -> None:
        self.settings = settings
        self.use_async = use_async

        # mongo specific settings
        self.mongo_host = self.settings.MONGO_HOST
        self.mongo_database_name = self.settings.MONGO_DATABASE_NAME
        self.mongo_collection = self.settings.MONGO_COLLECTION_NAME

        # do we have an SSH key
        self.use_auth_path = False

        # auth path with .ssh key
        self.auth_path = Path.home().joinpath(".ssh/atlas-mongo.pem")

        self.client: MongoClient[dict[str, Any]] = None

        # if we have an auth path, use it. This is an ssh key probabaly used locally
        if self.auth_path.exists():
            # will provide auth path in client setup
            self.use_auth_path = True
            self.mongo_uri = f"mongodb+srv://{self.mongo_host}/{self.mongo_database_name}?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
            if self.use_async:
                self.client = AsyncIOMotorClient(self.mongo_uri, tls=True, tlsCertificateKeyFile=str(self.auth_path))
            else:
                self.client = MongoClient(self.mongo_uri, tls=True, tlsCertificateKeyFile=str(self.auth_path))

        # in production use, env vars to get client
        # @note - this is stored in Notion
        elif os.environ.get("MONGOUSER") and os.environ.get("MONGOPASSWORD"):
            self.mongo_uri = f"mongodb+srv://{os.environ['MONGOUSER']}:{os.environ['MONGOPASSWORD']}@{self.mongo_host}/{self.mongo_database_name}?retryWrites=true&w=majority"
            if self.use_async:
                self.client = AsyncIOMotorClient(self.mongo_uri)
            else:
                self.client = MongoClient(self.mongo_uri)
        else:
            raise AuthenticationError(f"can not authenticate {self.mongo_host} with credentials")
        logger.info(self.client.server_info())

    def get_client(self) -> AsyncIOMotorClient | MongoClient[dict[str, Any]]:
        return self.client

    def get_database(self) -> Any:
        return self.client[self.mongo_database_name]

    def get_collection(self) -> Any:
        return self.get_database()[self.mongo_collection]
