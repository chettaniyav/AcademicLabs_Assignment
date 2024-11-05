from pymongo import MongoClient


def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    return client["clinical_trials_db"]


def insert_studies(db, studies):
    collection = db["studies"]
    collection.insert_many(studies)
