from typing import Any
from pymongo import MongoClient
from g4.mongo import AuthenticationError, Mongo
from g4.config import Settings
from pymongo.database import Database
import pytest
import asyncio
from pathlib import Path

async def get_motor_server_info(client: MongoClient[dict[str, Any]]) -> dict[str, Any]:
    return await client.server_info()


def test_mongo_client():
    settings = Settings()
    mongo_async = Mongo(settings)
    mongo_sync = Mongo(settings, use_async=False)
    async_client = mongo_async.get_client()

    # handle the async part
    loop = asyncio.get_event_loop()
    server_info = loop.run_until_complete(get_motor_server_info(async_client))
    assert server_info["ok"] == 1.0

    # use mongo client for everything else
    sync_client = mongo_sync.get_client()
    server_info_sync = sync_client.server_info()
    assert server_info_sync["ok"] == 1.0

    # get database
    database = mongo_sync.get_database()
    assert isinstance(database, Database)
    assert database.client.address[0] == "germlinegenegateway-shard-00-02.uvdtl.mongodb.net"
    assert database.client.address[1] == 27017

    # get imgt collection
    collection = mongo_sync.get_collection("imgt")
    assert collection.find_one()["source"] == "imgt"

    # get custom collection
    collection = mongo_sync.get_collection("custom")
    assert collection.find_one()["source"] == "custom"


def test_authentication_errors(monkeypatch):
    # test auth error
    monkeypatch.setenv("MONGOUSER", "test")
    monkeypatch.setenv("MONGOPASSWORD", "test")
    settings = Settings()
    with pytest.raises(AuthenticationError):
        Mongo(settings, use_async=False)

    monkeypatch.delenv("MONGOUSER")
    monkeypatch.delenv("MONGOPASSWORD")
    with pytest.raises(AuthenticationError):
        Mongo(settings, use_async=False, dot_env_path=Path("tests/unit/.env"))
