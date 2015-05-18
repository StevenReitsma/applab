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
            a = db.coll('achievements').find({'aid': t['aid']}, sort=[('name', db.ASCENDING)])
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
            a = db.coll('achievements').find({'aid': t['aid']}, sort=[('name', db.ASCENDING)])
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
            t = db.coll('unlocked').find({'aid': a['_id']})
            if t.count() < 1:
                result.append(a)

        print results
        return result


class UserProfile(restful.Resource):
    @require_appkey
    def get(self):
        uid = request.json['uid']
        return getByUID(uid)

    def getByUID(self, uid):
        db = DB()
        users = db.coll('users').find({'_id': ObjectId(uid)})

        if users.count() != 1:
            abort(404)

        result = users[0]
        level = 1
        points = 0
        count = 0

        unlocked = db.coll('progress').find({'uid': uid, 'unlocked': True})
        all_unlocked_achievements = []

        for t in unlocked:
            a = db.coll('achievements').find({'_id': ObjectId(t['aid'])}, sort=[('name', db.ASCENDING)])
            points += a[0]['score']
            count += 1
            all_unlocked_achievements.append(a)

        unlocked_achievements_by_rarity = sorted(all_unlocked_achievements, key=lambda a: a['score'], reverse=True)

        result['rare'] = list(islice(unlocked_achievements_by_rarity, 3))
        result['points'] = points
        result['level'] = 1  # TODO
        result['percent'] = 50  # TODO
        result['member_for_days'] = (datetime.datetime.utcnow() - result['date']).days
        result['achievement_count'] = count
        del result['password']

        return result


class UserProfileDefault(restful.Resource):
    @require_appkey
    def get(self):
        key = request.args.get('key')
        uid = query.current_uid(key)
        return UserProfile().getByUID(uid)


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

        return query.api_key_valid(key)


class Ranking(restful.Resource):
    @require_appkey
    def get(self):
        db = DB()

        result = db.coll('users').find()
        user_scores = {}
        achievement_count = {}

        for user in result:
            unlocked = db.coll('progress').find({'uid': user['_id'], 'unlocked': True})

            score = 0
            for u in unlocked:
                a = db.coll('achievements').find({'_id': ObjectId(u['aid'])})
                score += a[0]['score']

            user_scores[str(user['_id'])] = score
            achievement_count[str(user['_id'])] = unlocked.count()

        scores = sorted(user_scores.items(), key=operator.itemgetter(1), reverse=True)

        ids = [s[0] for s in scores]
        scores = [s[1] for s in scores]

        counts = [achievement_count[d] for d in ids]
        d = {"uid" : ids, "score": scores, "counts":counts}
        keys = ["uid", "score","counts"]
        v = [dict(zip(keys, vals)) for vals in zip(*(d[k] for k in keys))]
        return v


api.add_resource(AchievementsList, '/achievements/all')
api.add_resource(AchievementsUnlocked, '/achievements/unlocked')
api.add_resource(AchievementsProgress, '/achievements/progress')
api.add_resource(AchievementsOther, '/achievements/other')
api.add_resource(UserProfile, '/users/profile/<int:id>')
api.add_resource(UserProfileDefault, '/users/profile')
api.add_resource(Watchlist, '/users/watchlist')
api.add_resource(Login, '/login')
api.add_resource(Validate, '/validate')
api.add_resource(Ranking, '/ranking')

if __name__ == "__main__":
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()