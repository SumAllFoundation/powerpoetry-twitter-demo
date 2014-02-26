import functools
import json

from flask import abort, g, request, Response
from flask_peewee.rest import RestAPI, RestrictOwnerResource, RestResource, UserAuthentication
from flask_peewee.utils import check_password, make_password
from werkzeug import MultiDict

from ..app import app
from .auth import auth
from .model import User, Tweet
from .util import transaction


class ApiException(Exception):

    def __init__(self, message, code=None):
        self.code = code or (hash(message) % 500)
        super(ApiException, self).__init__(message)


class BadRequestException(Exception):
    pass


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

    pass


api = RestAPI(app)
user_auth = RestAuthentication(auth)
api.register(User, UserResource, auth=user_auth)
api.register(Tweet, TweetResource)
api.setup()
