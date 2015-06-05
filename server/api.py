from flask import Flask, json, make_response
from flask.ext import restful
from flask_restful import reqparse
from functools import wraps
from flask import request, abort
import query
from db import DB
from bson.json_util import dumps
import datetime
from bson.objectid import ObjectId
import random
import string
from itertools import islice

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import numpy as np
import operator


def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp


DEFAULT_REPRESENTATIONS = {'application/json': output_json}

parser = reqparse.RequestParser()
app = Flask(__name__)
api = restful.Api(app)
api.representations = DEFAULT_REPRESENTATIONS


def get_level(points):
    return int(0.67 * np.sqrt(points))

def get_min_points_for_level(level):
    return np.ceil((level / 0.67)**2)

def get_remainder(points):
    cur_level = get_level(points)
    total_for_next_level = get_min_points_for_level(cur_level+1)

    return total_for_next_level - points

def get_percent_next_level(points):
    cur_level = get_level(points)
    total_for_next_level = get_min_points_for_level(cur_level+1)
    to_go = total_for_next_level - points

    return round((1 - (to_go / total_for_next_level)) * 100.)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


# The actual decorator function
def require_appkey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.args.get('key') and query.api_key_valid(request.args.get('key')):
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


class AchievementsList(restful.Resource):
    def get(self):
        db = DB()
        achievements = db.coll('achievements').find(sort=[('name', db.ASCENDING)])
        return achievements


class AchievementsUnlocked(restful.Resource):
    @require_appkey
    def get(self):
        key = request.args.get('key')
        uid = query.current_uid(key)
        db = DB()

        unlocked = db.coll('progress').find({'uid': uid, 'unlocked': True})
        result = []
        for t in unlocked:
            a = db.coll('achievements').find({'_id': t['aid']}, sort=[('name', db.ASCENDING)])
            result.append(a[0])

        return result

class AchievementsOtherUnlocked(restful.Resource):
    @require_appkey
    def get(self):
        db = DB()
        name = request.args['name']
        uid = db.coll('users').find_one({'name':name})['_id']

        unlocked = db.coll('progress').find({'uid': uid, 'unlocked': True})

        result = []

        for t in unlocked:
            a = db.coll('achievements').find({'_id': t['aid']}, sort=[('name', db.ASCENDING)])
            result.append(a[0])

        return result


class AchievementsProgress(restful.Resource):
    @require_appkey
    def get(self):
        key = request.args.get('key')
        uid = query.current_uid(key)

        db = DB()
        unlocked = db.coll('progress').find({'uid': uid, 'unlocked': False})

        result = []

        for t in unlocked:
            a = db.coll('achievements').find({'_id': t['aid']}, sort=[('name', db.ASCENDING)])
            result.append(a[0])

        return result


class AchievementsOther(restful.Resource):
    @require_appkey
    def get(self):
        key = request.args.get('key')
        uid = query.current_uid(key)

        db = DB()
        all_achievements = db.coll('achievements').find(sort=[('name', db.ASCENDING)])

        result = []

        for a in all_achievements:
            t = db.coll('progress').find({'aid': a['_id'], 'uid': uid, 'unlocked': True})
            if t.count() < 1:
                result.append(a)

        return result


class UserProfile(restful.Resource):
    @require_appkey
    def get(self):
        uid = request.json['uid']
        return self.getByUID(uid)

    def getByUID(self, uid):
        db = DB()
        users = db.coll('users').find({'_id': ObjectId(uid)})

        if users.count() != 1:
            abort(404)

        result = users[0]
        points = 0
        count = 0

        unlocked = db.coll('progress').find({'uid': uid, 'unlocked': True})
        all_unlocked_achievements = []

        for t in unlocked:
            a = db.coll('achievements').find_one({'_id': t['aid']}, sort=[('name', db.ASCENDING)])
            points += a['score']
            count += 1
            all_unlocked_achievements.append(a)

        # Add masteries to score
        counters = db.coll('counters').find({'uid': uid})

        for c in counters:
            if c['name'] == 'running_total':
                points += np.floor(c['value'] / 10.) * 10
            elif c['name'] == 'cycling_total':
                points += np.floor(c['value'] / 50.) * 10
            elif c['name'] == 'pushups_total':
                points += np.floor(c['value'] / 100.) * 10

        unlocked_achievements_by_rarity = sorted(all_unlocked_achievements, key=lambda b: b['score'], reverse=True)

        result['rare'] = list(islice(unlocked_achievements_by_rarity, 2))
        result['points'] = points
        result['level'] = get_level(points)
        result['percent'] = get_percent_next_level(points)
        result['remainder'] = get_remainder(points)
        result['member_for_days'] = (datetime.datetime.utcnow() - result['date']).days
        result['achievement_count'] = count
        del result['password']
        return result


class InsertClick(restful.Resource):
    @require_appkey
    def post(self):
        db = DB()
        key = request.args.get('key')
        uid = query.current_uid(key)
        page = request.json['page']
        details = request.json['details']
        db.coll('clicks').insert({'uid':uid,'page':page,'date':datetime.datetime.utcnow(),'details':details})
        return request.json


class UserProfileDefault(restful.Resource):
    @require_appkey
    def get(self):
        key = request.args.get('key')
        uid = query.current_uid(key)
        return UserProfile().getByUID(uid)

    @require_appkey
    def post(self):
        db = DB()
        key = request.args.get('key')
        uid = query.current_uid(key)
        anonymous = request.json['anonymous']
        print anonymous
        db.coll('users').update({'_id':uid},{"$set":{'anonymous':anonymous}})
        return request.json


class Watchlist(restful.Resource):
    @require_appkey
    def get(self):
        key = request.args.get('key')
        uid = query.current_uid(key)

        db = DB()
        wl = db.coll('watchlist').find({'uid': uid}, sort=[('date', db.DESCENDING)])

        result = []

        for a in wl:
            am = db.coll('achievements').find({'_id': ObjectId(a['aid'])})
            result.append({'name': am[0]['name'], 'description': am[0]['description'], 'aid': a['aid']})

        return result

    @require_appkey
    def post(self):
        key = request.args.get('key')
        uid = query.current_uid(key)
        aid = request.json['aid']

        db = DB()
        db.coll('watchlist').insert({'uid': uid, 'aid': aid, 'date': datetime.datetime.utcnow()})

        return request.json

    @require_appkey
    def delete(self):
        key = request.args.get('key')
        uid = query.current_uid(key)
        aid = request.args.get('aid')

        db = DB()
        db.coll('watchlist').remove({'uid': uid, 'aid': aid})

        return {}


class Login(restful.Resource):
    def post(self):
        email = request.json['email']
        pwd = request.json['password']

        db = DB()
        result = db.coll('users').find({'email': email, 'password': pwd})

        if result.count() < 1:
            abort(403)

        token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(48))

        # Remove old tokens
        db.coll('tokens').remove({'uid': result[0]['_id']})

        # Insert new
        db.coll('tokens').insert({'uid': result[0]['_id'], 'token': token, 'date': datetime.datetime.utcnow()})

        return {"token": token}


class Validate(restful.Resource):
    def get(self):
        key = request.args.get('key')

        return {'valid': query.api_key_valid(key)}


class Ranking(restful.Resource):
    @require_appkey
    def get(self):
        db = DB()

        result = db.coll('users').find({'anonymous':False})
        user_scores = {}
        achievement_count = {}

        for user in result:
            unlocked = db.coll('progress').find({'uid': user['_id'], 'unlocked': True})

            score = 0
            for u in unlocked:
                a = db.coll('achievements').find({'_id': ObjectId(u['aid'])})
                score += a[0]['score']

            # Add masteries to score
            counters = db.coll('counters').find({'uid': user['_id']})

            for c in counters:
                if c['name'] == 'running_total':
                    score += np.floor(c['value'] / 10.) * 10
                elif c['name'] == 'cycling_total':
                    score += np.floor(c['value'] / 50.) * 10
                elif c['name'] == 'pushups_total':
                    score += np.floor(c['value'] / 100.) * 10

            user_scores[str(user['_id'])] = score
            achievement_count[str(user['_id'])] = unlocked.count()

        scores = sorted(user_scores.items(), key=operator.itemgetter(1), reverse=True)

        ids = [s[0] for s in scores]
        scores = [s[1] for s in scores]
        names = [db.coll('users').find_one({'_id':ObjectId(uid)})['name'] for uid in ids]
        counts = [achievement_count[d] for d in ids]
        d = {"uid" : ids, "score": scores, "counts":counts, "names": names}
        keys = ["uid", "score","counts", "names"]
        v = [dict(zip(keys, vals)) for vals in zip(*(d[k] for k in keys))]
        return v

class Dashboard(restful.Resource):
    @require_appkey
    def get(self):
        db = DB()

        key = request.args.get('key')
        uid = query.current_uid(key)

        response = {}

        recent = db.coll('progress').find({'uid': uid, 'unlocked': True}, sort=[('date', db.DESCENDING)]).limit(3)
        counters = db.coll('counters').find({'uid': uid})

        recent_achievements = []
        for r in recent:
            a = db.coll('achievements').find({'_id': ObjectId(r['aid'])})
            recent_achievements.append(a[0])

        # Initial values
        response['running_level'] = 1
        response['cycling_level'] = 1
        response['pushups_level'] = 1

        response['running'] = 0
        response['cycling'] = 0
        response['pushups'] = 0

        for c in counters:
            if c['name'] == 'running_total':
                response['running_level'] = np.ceil((c['value']+1) / 10.)
                response['running'] = (c['value'] - 10 * (response['running_level']-1)) / 10. * 100.
            elif c['name'] == 'cycling_total':
                response['cycling_level'] = np.ceil((c['value']+1) / 50.)
                response['cycling'] = (c['value'] - 50 * (response['cycling_level']-1)) / 50. * 100.
            elif c['name'] == 'pushups_total':
                response['pushups_level'] = np.ceil((c['value']+1) / 100.)
                response['pushups'] = (c['value'] - 100 * (response['pushups_level']-1)) / 100. * 100.

        recommended = AchievementRecommender(uid)

        response['recent'] = recent_achievements
        response['recommended'] = recommended

        username = db.coll('users').find_one({'_id': ObjectId(uid)})['name'].split()[0]

        response['name'] = username

        return response
class NonFriends(restful.Resource):
    @require_appkey
    def get(self):
        db = DB()
        key = request.args.get('key')
        uid = query.current_uid(key)
        friends = db.coll('users').find_one({'_id':uid})['friends']
        users = db.coll('users').find({'anonymous':False})
        list = []
        for user in users:
            if str(user['_id']) not in friends and user['_id'] != uid:
                list.append(user['name'])
        return list

class Friend(restful.Resource):
    @require_appkey
    def get(self):
        db = DB()
        name = request.args['name']
        uid = db.coll('users').find_one({'name':name})['_id']
        return UserProfile().getByUID(uid)

class Friends(restful.Resource):
    @require_appkey
    def get(self):
        db = DB()
        user = UserProfileDefault().get()
        friends = []
        for friend in user['friends']:
            friends.append(UserProfile().getByUID(friend)['name'])
        return friends

    @require_appkey
    def post(self):
        db = DB()
        key = request.args.get('key')
        uid = query.current_uid(key)
        name = request.json['name']
        friends = db.coll('users').find_one({'_id':uid})['friends']
        friend = db.coll('users').find_one({'name':name})['_id']
        friends.append(str(friend))
        db.coll('users').update({'_id':uid},{'$set': {"friends":friends}})
        return request.json

    @require_appkey
    def delete(self):
        db = DB()
        key = request.args.get('key')
        uid = query.current_uid(key)
        name = request.args.get('names')
        friendId = db.coll('users').find_one({'name':name})['_id']
        friends = db.coll('users').find_one({'_id':uid})['friends']
        friends.remove(str(friendId))
        db.coll('users').update({'_id':uid},{'$set': {"friends":friends}})
        return {}


def updateCounters(count,uid,activity):
    db = DB()
    a = db.coll('counters').find_one({'uid':uid, 'name':activity+"_total"})
    if a is not None:
        db.coll('counters').update({'uid':uid, 'name':activity+"_total"},{'$set':{'value':a['value']+count}})
    else:
        db.coll('counters').insert({'uid':uid, 'name':activity+"_total",'value':count})


def AchievementRecommender(uid):
    db = DB()
    progress = list(db.coll('progress').find({'uid':uid, 'unlocked':False}))
    achievements = []
    if len(progress) > 2:
        ids = np.random.choice(progress,3,replace=False)#Select 3 random progress achievements
        for id in ids:
            achievements.append(db.coll('achievements').find_one({'_id':id['aid']})) #find the correct achievements
    else:
        progid = []
        if progress != []:
            for p in progress:
                achievements.append(db.coll('achievements').find_one({'_id':p['aid']}))
                progid.append(p['aid'])
        completed = db.coll('progress').find({'unlocked':True})
        for c in completed:
            progid.append(c['aid'])
        achiev = list(db.coll('achievements').find({'_id':{"$nin":progid}})) #achievements that are not already recommended
        tempAchiev = []
        for a in achiev:
            if a['requirements']['value'] <= 5:
                tempAchiev.append(a)
        if len(tempAchiev) > 3-len(achievements): #check whether there are enough achievements in tempachiev
            choice = np.random.choice(tempAchiev,(3-len(achievements)),replace=False)#random achievements that are easy to get
        elif len(achiev) > 3-len(achievements): #check whether there are enough remaining achievements overall
            choice = np.random.choice(achiev,(3-len(achievements)),replace=False)
        else:
            choice = achiev
        achievements = np.append(achievements,choice)
    return achievements


class UpdateAchievements(restful.Resource):
    #Need in arguments activity, speed, count
    @require_appkey
    def post(self):
        db = DB()
        key = request.args.get('key')
        uid = query.current_uid(key)
        activity = request.json['activity']
        speed = request.json['speed']
        count = request.json['count']
        updateCounters(count,uid,activity)
        Progress = db.coll('progress').find({'uid':uid})
        inProgress = []
        unlocked = []
        db.coll('users').update({'_id':uid},{"$set":{'activity_today':True}})
        for p in Progress:
            inProgress.append(p['aid'])
            if p['unlocked'] == False:
                if p['name'] == "daily_" + activity:#for daily activities
                    if not p['updated_today']:
                        if count >= p['remaining']:
                            if p['days_left'] == 1:
                                db.coll('progress').update({'uid':uid,'aid':p['aid']},{'$set':{'unlocked':True}})
                                unlocked.append(db.coll('achievements').find_one({'_id':p['aid']})['name'])
                            else:
                                db.coll('progress').update({'uid':uid,'aid':p['aid']},{'$set':{'days_left':p['days_left']-1,'updated_today':True}})
                        else:
                            db.coll('progress').update({'uid':uid,'aid':p['aid']},{'$set':{'remaining':p['remaining']-count}})
                elif p['name']!= "no_activity":
                    a = db.coll('achievements').find_one({'_id':p['aid']})
                    if a['requirements']['value'] < db.coll('counters').find_one({'uid':uid,'name':activity+"_total"})['value']:
                        db.coll('progress').update({'uid':uid,'aid':p['aid']},{'$set':{'unlocked':True}})
                        unlocked.append(a['name'])
                else:
                    db.coll('progress').remove({'aid':p['aid'],'uid':p['uid']})


        achievements = db.coll('achievements').find({'_id':{"$nin":inProgress}}) #achievements that are not in progress
        for a in achievements:
            requirements = a['requirements']
            name = requirements['name']
            if name == "daily_"+activity: #for daily activities
                if count >= requirements['value']:
                    if a['days_total'] == 1:
                        db.coll('progress').insert({'aid':a['_id'],'uid':uid,'unlocked':True})
                        unlocked.append(a['name'])
                    else:
                        db.coll('progress').insert({'aid':a['_id'],'uid':uid,'unlocked':False,'days_left':a['days_total']-1,'name':"daily_"+activity, 'remaining': requirements['value'],'updated_today':True})
                else:   #for multiple entries in a day
                    db.coll('progress').insert({'aid':a['_id'],'uid':uid,'unlocked':False,'days_left':a['days_total'],'name':"daily_"+activity, 'remaining': requirements['value']-count,'updated_today':False})

            elif name==activity+"_total":  #for total activities
                if count >= requirements['value']:
                    db.coll('progress').insert({'aid':a['_id'],'uid':uid,'unlocked':True})
                    unlocked.append(a['name'])
                else:
                    db.coll('progress').insert({'aid':a['_id'],'uid':uid,'unlocked':False, 'name':activity + "_total"})
            elif name=="speed_" + activity:
                if count >= requirements['value'] and speed >= requirements['speed']:
                    db.coll('progress').insert({'aid':a['_id'],'uid':uid,'unlocked':True})
                    unlocked.append(a['name'])

        return {"unlocked":unlocked}


api.add_resource(InsertClick, '/insertclick')
api.add_resource(AchievementsList, '/achievements/all')
api.add_resource(AchievementsUnlocked, '/achievements/unlocked')
api.add_resource(AchievementsOtherUnlocked, '/achievements/unlocked_other')
api.add_resource(AchievementsProgress, '/achievements/progress')
api.add_resource(AchievementsOther, '/achievements/other')
api.add_resource(UserProfile, '/users/profile/<int:id>')
api.add_resource(UserProfileDefault, '/users/profile')
api.add_resource(Watchlist, '/users/watchlist')
api.add_resource(Login, '/login')
api.add_resource(Validate, '/validate')
api.add_resource(Ranking, '/ranking')
api.add_resource(Dashboard, '/dashboard')
api.add_resource(Friends, '/users/friends')
api.add_resource(Friend, '/users/friends/friend')
api.add_resource(NonFriends, '/nonfriends')
api.add_resource(UpdateAchievements, '/updateachievements')


if __name__ == "__main__":
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()