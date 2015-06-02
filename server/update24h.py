__author__ = 'Robbert'
from db import DB
from bson.objectid import ObjectId

def inactive():
    db = DB()
    users = db.coll('users').find()
    for u in users:
        if u['activity_today']:
            db.coll('users').update({'_id':u['_id']},{"$set":{'activity_today':False}})
            db.coll('progress').remove({'name':"no_activity",'uid':u['_id']})
        else:
            lazy_achievs = db.coll('achievements').find({'requirements.name':"no_activity"})
            for a in lazy_achievs:
                achiev = db.coll('progress').find_one({'aid':a['_id'],'uid':u['_id']})
                if achiev != None:
                    if not achiev['unlocked']:
                        if achiev['days_left'] == 1:
                            db.coll('progress').update({'_id':achiev['_id']},{"$set":{'unlocked':True}})
                        else:
                            db.coll('progress').update({'_id':achiev['_id']},{"$set":{'days_left':achiev['days_left']-1}})
                else:
                    if a['days_total'] == 1:
                        db.coll('progress').insert({'aid':a['_id'],'uid':u['_id'],'unlocked':True})
                    else:
                        db.coll('progress').insert({'aid':a['_id'],'uid':u['_id'],'unlocked':False,'days_left':a['days_total']-1,'name':"no_activity"})


if __name__ == "__main__":
    db = DB()
    progress = db.coll('progress').find({'requirements.name':{"$ne":"no_activity"}})
    for p in progress:
        if not p['unlocked']:
            if p['name'] == "daily_cycling" or p['name'] == "daily_running" or p['name'] == "daily_pushups":
                if p['updated_today']:
                    db.coll('progress').update({'_id':p['_id']},{"$set":{'updated_today':False}})
                else:
                    a = db.coll('achievements').find_one({'_id':p['aid']})
                    if a['requirements']['value'] is not p['remaining'] or a['total_days'] is not p['days_left']:
                        db.coll('progress').remove({'_id':p['_id']})
    inactive()