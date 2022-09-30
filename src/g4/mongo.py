# pyright: reportMissingTypeStubs=true
import logging
import os
from typing import Any

from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from g4.config import Settings

logger = logging.getLogger("Mongo")


class AuthenticationError(Exception):
    def __init__(self, exception_str: str) -> None:
        self.exception_str = exception_str

    def __str__(self) -> str:
        return self.exception_str


class Mongo:
    def __init__(self, settings: Settings, use_async: bool = True, dot_env_path: Path = Path(".env")) -> None:
        self.settings = settings

        # mongo specific settings
        self.mongo_host = self.settings.MONGO_HOST
        self.mongo_database_name = self.settings.MONGO_DATABASE_NAME
        self.dot_env_path = dot_env_path

        # do we have an SSH key
        self.use_auth_path = False

        # should we use async client
        self.use_async = use_async

        # boolean to check if we have API env variables
        self.has_api_key = False

        # setup nothing instance
        self.client: MongoClient[dict[str, Any]] = MongoClient()

        # in production use, env vars to get client
        if not "MONGOUSER" in os.environ and not "MONGOPASSWORD" in os.environ:
            logger.info("Loading environment variables form .env")
            self.has_api_key = self.load_env()
        else:
            logger.info("Using environment variables")
        self.mongo_uri = f"mongodb+srv://{os.environ['MONGOUSER']}:{os.environ['MONGOPASSWORD']}@{self.mongo_host}/{self.mongo_database_name}?retryWrites=true&w=majority"
        self.client = MongoClient(self.mongo_uri)
        try:
            self.client.server_info()
        except OperationFailure:
            error = AuthenticationError(f"Invalid Mongo Credentials, MONGOUSER and MONGOPASSWORD are incorrect")
            logger.error(error.__str__())
            raise error
        self.async_client = AsyncIOMotorClient(self.mongo_uri)

    def load_env(self) -> bool:
        try:
            from dotenv import load_dotenv  # type: ignore

            # this loads .env file if we have one
            load_dotenv(self.dot_env_path)
            if "MONGOUSER" in os.environ and "MONGOPASSWORD" in os.environ:
                logger.info("Loaded environment variables")
                return True
            else:
                error = AuthenticationError("Missing environment variables, MOGNOUSER and MONGOPASSWORD")
                logger.error(error.__str__())
                raise error
        except ImportError:
            error = ImportError(
                "Missing dotenv module, please install dotenv module or have  MONGOUSER and MONGOPASSWORD environment variables"
            )
            raise error

    def get_client(self) -> AsyncIOMotorClient | MongoClient[dict[str, Any]]:
        if self.use_async:
            return self.async_client
        return self.client

    def get_database(self) -> Any:
        _client = self.get_client()
        return _client[self.mongo_database_name]

    def get_collection(self, collection_name: str) -> Any:
        return self.get_database()[collection_name]
