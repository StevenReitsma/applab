import pymongo
from pymongo import MongoClient

class DB():
	_instance = None
	ASCENDING = pymongo.ASCENDING
	DESCENDING = pymongo.DESCENDING

	def __init__(self):
		self.client = MongoClient('localhost', 27017)
		self.db = self.client.athlos

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(DB, cls).__new__(cls, *args, **kwargs)

		return cls._instance

	def coll(self, name):
		return self.db[name]
