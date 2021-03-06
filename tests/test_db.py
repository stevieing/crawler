from datetime import datetime

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from crawler.db import (
    copy_collection,
    create_import_record,
    create_mongo_client,
    get_mongo_collection,
    get_mongo_db,
)


def test_create_mongo_client(config):
    assert type(create_mongo_client(config)) == MongoClient


def test_get_mongo_db(mongo_client):
    config, mongo_client = mongo_client
    assert type(get_mongo_db(config, mongo_client)) == Database


def test_get_mongo_collection(mongo_database):
    _, mongo_database = mongo_database
    collection_name = "test_collection"
    test_collection = get_mongo_collection(mongo_database, collection_name)
    assert type(test_collection) == Collection
    assert test_collection.name == collection_name


def test_copy_collection(mongo_database):
    _, mongo_database = mongo_database
    collection_name = "test_collection"
    collection = get_mongo_collection(mongo_database, collection_name)
    _ = collection.insert_one({"x": 1})

    copy_collection(mongo_database, collection)

    assert f"{collection_name}_{datetime.now().strftime('%y%m%d_%H%M')}" in [
        collection["name"] for collection in mongo_database.list_collections()
    ]


def test_create_import_record(freezer, mongo_database):
    config, mongo_database = mongo_database
    import_collection = mongo_database["imports"]

    docs = [{"x": 1}, {"y": 2}, {"z": 3}]
    errors = ["error1", "error2"]

    for centre in config.CENTRES:
        now = datetime.now().isoformat(timespec="seconds")
        result = create_import_record(import_collection, centre, len(docs), "test", errors)
        import_doc = import_collection.find_one({"_id": result.inserted_id})

        assert import_doc["date"] == now
        assert import_doc["centre_name"] == centre["name"]
        assert import_doc["csv_file_used"] == "test"
        assert import_doc["number_of_records"] == len(docs)
        assert import_doc["errors"] == errors
