import pymongo

HOST = 'localhost'
PORT = 27017
DB = "01.02.2023"

class DBClient():

    def __init__(self):
        self._client = pymongo.MongoClient(f"mongodb://{HOST}:{PORT}/")
        self.db = self._client["open_edr"]
        self.col = self.db[DB]

    def import_item(self, item):
        self.col.insert_one(item)