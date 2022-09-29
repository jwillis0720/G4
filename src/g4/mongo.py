# pyright: reportMissingTypeStubs=true
import logging
import os
from pathlib import Path
from typing import Any

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
    def __init__(
        self,
        settings: Settings,
        use_async: bool = True,
        key_path: str | Path = Path.home().joinpath(".ssh/atlas-mongo.pem"),
    ) -> None:
        self.settings = settings
        self.use_async = use_async

        # mongo specific settings
        self.mongo_host = self.settings.MONGO_HOST
        self.mongo_database_name = self.settings.MONGO_DATABASE_NAME

        # do we have an SSH key
        self.use_auth_path = False

        # auth path with .ssh key
        self.auth_path = Path(key_path)

        # setup nothing instance
        self.client: MongoClient[dict[str, Any]] = MongoClient()

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
        else:
            if not "MONGOUSER" in os.environ and not "MONGOPASSWORD" in os.environ:
                self.load_env()
            self.mongo_uri = f"mongodb+srv://{os.environ['MONGOUSER']}:{os.environ['MONGOPASSWORD']}@{self.mongo_host}/{self.mongo_database_name}?retryWrites=true&w=majority"
            if self.use_async:
                self.client = AsyncIOMotorClient(self.mongo_uri)
            else:
                self.client = MongoClient(self.mongo_uri)
                try:
                    self.client.server_info()
                except OperationFailure:
                    error = AuthenticationError(f"Invalid Mongo Credentials, MONGOUSER and MONGOPASSWORD are incorrect")
                    logger.error(error.__str__())
                    raise error

    def load_env(self) -> None:
        try:
            from dotenv import load_dotenv  # type: ignore

            load_dotenv()
            if "MONGOUSER" in os.environ and "MONGOPASSWORD" in os.environ:
                logger.info("Loaded environment variables")
            else:
                error = AuthenticationError("Missing environment variables, MOGNOUSER and MONGOPASSWORD")
                logger.error(error.__str__())
                raise error
        except ImportError:
            error = AuthenticationError(
                "Missing dotenv module, please install dotenv module or have  MONGOUSER and MONGOPASSWORD environment variables"
            )
            logger.error(error.__str__())
            raise error

    def get_client(self) -> AsyncIOMotorClient | MongoClient[dict[str, Any]]:
        return self.client

    def get_database(self) -> Any:
        return self.client[self.mongo_database_name]

    def get_collection(self, collection_name: str) -> Any:
        return self.get_database()[collection_name]
