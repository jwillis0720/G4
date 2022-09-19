from pymongo import MongoClient
from pathlib import Path
from typing import List
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os

logger = logging.getLogger("Mongo")


class AuthenticationError(Exception):
    pass


class Mongo:
    def __init__(self, use_async:bool=True):
        self._host = "germlinegenegateway.uvdtl.mongodb.net"
        self._database_str = "g3"
        self._auth_path = Path.home().joinpath(".ssh/atlas-mongo.pem")
        if self._auth_path.exists():
            self._uri = f"mongodb+srv://{self.host}/{self._database_str}?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
        elif os.environ.get("MONGOUSER") and os.environ.get("MONGOPASSWORD"):
            self._uri = f"mongodb+srv://{os.environ['MONGOUSER']}:{os.environ['MONGOPASSWORD']}@{self.host}/{self._database_str}?retryWrites=true&w=majority"
        else:
            raise AuthenticationError(f"can not authenticate {self._host}")
        if use_async:
            if self._auth_path.exists():
                logger.info("Using certificate and async client")
                self._client = AsyncIOMotorClient(self._uri, tls=True, tlsCertificateKeyFile=str(self.auth_path))
            else:
                logger.info("Using and async client")
                self._client = AsyncIOMotorClient(self._uri)
        else:
            if self._auth_path.exists():
                logger.info("Using certificte")
                self._client = MongoClient(self._uri, tls=True, tlsCertificateKeyFile=str(self.auth_path))
            else:
                logger.info("Using password username")
                self._client = MongoClient(self._uri)

    @property
    def host(self) -> str:
        return self._host

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def auth_path(self) -> Path:
        return self._auth_path

    @auth_path.setter
    def auth_path(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"{path} .pem not found, can't connect. Place authentication in ~/.ssh")
        self._auth_path = path

    @property
    def client(self) -> MongoClient:
        return self._client

    def get_client(self) -> MongoClient:
        return self.client

    def get_database_names(self) -> List[str]:
        return self.client.list_database_names()
