from pymongo import MongoClient
from elasticsearch import Elasticsearch
import redis

## mongo config
#DB_URL

## es config
#ES_PORT

## nginx config


## redis config
KEY = 123456
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

## bot config
HOME = 'http://localhost:5000'





## db startup
client = MongoClient('mongodb://localhost:27017')
db = client['usrdb']

''' init
db.counter.drop()
db.create_collection('counter')
db.counter.insert_one({'_id':'users','sequence_value':20000})
'''

## redis startup
redis_client = redis.StrictRedis(host= REDIS_HOST, port= REDIS_PORT,)

## es startup
class elasticSearch():

    def __init__(self, index_type: str, index_name: str, ip="127.0.0.1"):

        # self.es = Elasticsearch([ip], http_auth=('elastic', 'password'), port=9200)
        self.es = Elasticsearch("http://localhost:9200")
        self.index_type = index_type
        self.index_name = index_name

    def create_index(self):
        if self.es.indices.exists(index=self.index_name) is True:
            self.es.indices.delete(index=self.index_name)
        self.es.indices.create(index=self.index_name, ignore=400)

    def delete_index(self):
        try:
            self.es.indices.delete(index=self.index_name)
        except:
            pass

    def get_doc(self, uid):
        return self.es.get(index=self.index_name, id=uid)

    def insert_one(self, doc: dict):
        self.es.index(index=self.index_name,
                      doc_type=self.index_type, body=doc)

    def insert_array(self, docs: list):
        for doc in docs:
            self.es.index(index=self.index_name,
                          doc_type=self.index_type, body=doc)

    def search(self, query, count: int = 30):
        dsl = {
            "query": {
                "bool": {
                    "filter": [{
                        "match": {"content": query}
                    }],
                    "must_not": [{ 
                        "term": {"title": None}
                    }],
                    ##"should": []
                }
            },
        }
        match_data = self.es.search(
            index=self.index_name, body=dsl, size=count)
        return match_data

    #考虑aggr
    def sift(self, pid, sort_type: str = 'time', size: int = 10):
        dsl = {
            "query": {
                "bool": {
                    "filter": [{
                        "term": {"_id": pid},
                        "match": {}
                    }]
                }
            }
        }