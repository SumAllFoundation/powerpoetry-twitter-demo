import functools
import json
import time

from flask import abort, g, jsonify, request, Response
from flask_peewee.rest import RestAPI, RestrictOwnerResource, RestResource
from flask_peewee.rest import Authentication, UserAuthentication
from flask_peewee.utils import check_password, make_password
from peewee import JOIN_LEFT_OUTER, fn
from werkzeug import MultiDict

from ..app import app
from .auth import auth
from .model import User, Tweet, Rating
from .util import transaction, wilson_confidence_column


class ApiException(Exception):

    def __init__(self, message, code=None):
        self.code = code or (hash(message) % 500)
        super(ApiException, self).__init__(message)


class BadRequestException(Exception):
    pass


class OpenAuthentication(Authentication):

    def __init__(self):
        super(OpenAuthentication, self).__init__(['PUT', 'DELETE'])


class RestAuthentication(UserAuthentication):

    def authorize(self):
        return bool(g.user)


class RestAPI(RestAPI):

    def response_auth_failed(self):
        return abort(403)


class RestResource(RestResource):

    def require_method(self, func, methods):
        outer = super(RestResource, self).require_method(func, methods)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                return transaction(outer)(*args, **kwargs)
            except ApiException, err:
                return self.response_api_exception({"error": err.message, "code": err.code})
        return inner

    def response_api_exception(self, data):
        kwargs = {} if request.is_xhr else {"indent": 2}
        return Response(json.dumps(data, **kwargs), 500, mimetype="application/json")

    def get_request_data(self):
        data = request.data or request.form.get("data") or ""

        try:
            return json.loads(data)
        except ValueError:
            if request.form:
                return MultiDict(request.form)
            raise BadRequestException()

    def create(self):
        try:
            instance = self.create_(self.get_request_data())
        except BadRequestException:
            return self.response_bad_request()
        else:
            return self.response(self.serialize_object(instance))

    def edit(self, obj):
        try:
            self.edit_(obj, self.get_request_data())
        except BadRequestException:
            return self.response_bad_request()
        else:
            return self.response(self.serialize_object(obj))

    def create_(self, data):
        instance, models = self.deserialize_object(data, self.model())
        self.save_related_objects(instance, data)
        return self.save_object(instance, data)

    def edit_(self, obj, data):
        obj, models = self.deserialize_object(data, obj)
        self.save_related_objects(obj, data)
        self.save_object(obj, data)
        return obj


class RestrictOwnerResource(RestrictOwnerResource, RestResource):

    def check_get(self, obj):
        return self.validate_owner(g.user, obj)


class UserResource(RestResource):

    exclude = ("password",)

    def create_(self, data):
        data["password"] = make_password(data.get("password"))
        return super(UserResource, self).create_(data)

    def edit_(self, obj, data):
        if "password" in data:
            current_password = data.pop("current_password", None)
            new_password = make_password(data.pop("password"))
            if check_password(current_password, obj.password):
                data["password"] = new_password

        return super(UserResource, self).edit_(obj, data)

    def check_get(self, obj=None):
        return g.user and (g.user.admin or obj == g.user)

    def check_put(self, obj):
        return g.user and (g.user.admin or obj == g.user)


class TweetResource(RestResource):

    def get_urls(self):
        return super(TweetResource, self).get_urls() + (
            ('/score/', self.top_scores),
            ('/score/<screen_name>/', self.user_score),
        )

    def get_query(self):
        return Tweet.select(Tweet, Rating).join(Rating, JOIN_LEFT_OUTER, on=(
            (Tweet.id == Rating.tweet) & (Rating.remote_addr == request.remote_addr)
        ).alias("user_rating"))

    def prepare_data(self, obj, data):
        data["user_rating"] = obj.user_rating.rating
        data["created_at"] = time.mktime(obj.created_at.timetuple()) * 1000
        return data

    def top_scores(self):
        score_col = fn.Sum(Tweet.score)
        count_col = fn.Count(Tweet.id)
        confidence_col = wilson_confidence_column(score_col, count_col, 100, 0.95)
        query = Tweet.select(
            Tweet.tweeted_by,
            score_col.alias('score'),
            count_col.alias('count'),
            confidence_col.alias('confidence')
        ).group_by(Tweet.tweeted_by).order_by(confidence_col.desc())

        return jsonify({
            "meta": {},
            "objects": [{
                "screen_name": row.tweeted_by,
                "score": row.score,
                "average": row.score / row.count,
                "confidence": row.confidence,
                "count": row.count
            } for row in query]
        })

    def user_score(self, screen_name):
        row = self.user_score_query(screen_name).get()
        return jsonify({
            "screen_name": row.tweeted_by,
            "score": row.score
        })

    def user_score_query(self, screen_name):
        return Tweet.select(
            Tweet.tweeted_by,
            fn.Count(Tweet.id).alias('count'),
            fn.Sum(Tweet.score).alias('score')
        ).where(
            Tweet.tweeted_by == screen_name
        ).group_by(Tweet.tweeted_by)


class RatingResource(RestResource):

    include_resources = {
        "tweet": TweetResource
    }

    def get_urls(self):
        return super(RatingResource, self).get_urls() + (
            ("/tweet/", self.top_tweets),
            ("/user/", self.top_users),
        )

    def create_(self, data):
        data["remote_addr"] = request.remote_addr
        rating = super(RatingResource, self).create_(data)
        rating.tweet.rating = (rating.tweet.rating * rating.tweet.rate_count) + rating.rating
        rating.tweet.rate_count += 1
        rating.tweet.rating /= rating.tweet.rate_count
        rating.tweet.save()
        return rating

    def edit_(self, obj, data):
        data["remote_addr"] = request.remote_addr
        return super(RatingResource, self).edit_(data)

    def top_tweets(self):
        score_col = fn.Sum(Rating.rating)
        count_col = fn.Count(Rating.id)
        confidence_col = wilson_confidence_column(score_col, count_col, 3, 0.99)

        query = Rating.select(
            Tweet,
            score_col.alias('rating'),
            count_col.alias('count'),
            confidence_col.alias('confidence')
        ).join(Tweet).group_by(Tweet.id).order_by(confidence_col.desc())

        return jsonify({
            "meta": {},
            "objects": [{
                "id": row.id,
                "text": row.text,
                "score": row.score,
                "tweeted_by": row.tweeted_by,
                "created_at": row.created_at,
                "rating": row.rating,
                "average": row.rating / row.count,
                "confidence": row.confidence,
                "count": row.count
            } for row in query]
        })

    def top_users(self):
        score_col = fn.Sum(Rating.rating)
        count_col = fn.Count(Rating.id)
        confidence_col = wilson_confidence_column(score_col, count_col, 3, 0.99)
        query = Rating.select(
            Tweet.tweeted_by,
            score_col.alias('rating'),
            count_col.alias('count'),
            confidence_col.alias('confidence')
        ).join(Tweet).group_by(Tweet.tweeted_by).order_by(confidence_col.desc())

        return jsonify({
            "meta": {},
            "objects": [{
                "screen_name": row.tweeted_by,
                "rating": row.rating,
                "average": row.rating / row.count,
                "confidence": row.confidence,
                "count": row.count
            } for row in query]
        })


api = RestAPI(app)
open_auth = OpenAuthentication()
user_auth = RestAuthentication(auth)

api.register(Tweet, TweetResource)
api.register(Rating, RatingResource, auth=open_auth)
api.register(User, UserResource, auth=user_auth)
api.setup()
