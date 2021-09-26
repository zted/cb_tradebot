import pymongo

import conf as cf
from data_models import TradeRecord


def start_mongo():
    client = pymongo.MongoClient(cf.MONGODB_URL)
    db = client[cf.MONGO_DB]
    assert cf.MONGO_COLLECTION in db.list_collection_names(), 'The collection specified could not be found in MongoDB'
    collection = db[cf.MONGO_COLLECTION]
    return collection


def insert(collection: pymongo.collection.Collection, trade: TradeRecord):
    res = collection.insert_one(trade.json())
    return res


def get_most_recent(collection: pymongo.collection.Collection):
    return collection.find_one({}, sort=[('_id', pymongo.DESCENDING)])
