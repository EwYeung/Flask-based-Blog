from config import *
from pymongo import ReturnDocument

def get_new_id(collection_id):
    newSequence = db.counter.find_one_and_update(
        {'_id':collection_id},
        {'$inc':{"sequence_value":1}},
        upsert = True,
        return_document=ReturnDocument.AFTER
    )

    return newSequence['sequence_value']
    
def get_data(query: dict):
     pass