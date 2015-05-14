from db import DB

def get_uid_by_api_key(key):
	db = DB()
	tokens = db.coll('tokens').find({'token': key})

	if tokens.count() > 0:
		return tokens[0]['uid']
	else:
		return -1

def current_uid(key):
	return get_uid_by_api_key(key)

def api_key_valid(key):
	db = DB()
	tokens = db.coll('tokens').find({'token': key})

	return tokens.count() > 0
