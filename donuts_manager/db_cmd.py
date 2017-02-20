import pymongo
import commands
from pymongo import MongoClient
import pprint


MONGO_HOST = 'pg01.prd.srv.hon.ar.internal'
MONGO_USER = 'donutsAdmin'
MONGO_PASSWORD = '12D0nuts78'
MONGO_DB = 'donuts'

mongo_uri = 'mongodb://%s:%s@%s' % (MONGO_USER, MONGO_PASSWORD, MONGO_HOST)
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client[MONGO_DB]


for i in mongo_db.users.find():
    pprint.pprint(i)

