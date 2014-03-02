from flask import abort, g, jsonify, redirect, request, render_template, url_for

from .app import api, app

from .core import redis_twitter_cache
from .core.model import Tweet, User
from .core.auth import auth
from .core.rest import api as rest_api, TweetResource, UserResource


user_resource = UserResource(rest_api, User, None, ["GET"])
tweet_resource = TweetResource(rest_api, Tweet, None, ["GET"])


@app.route("/")
def index():
    user_dict = None
    if g.user:
        user_dict = user_resource.serialize_object(g.user)
    return render_template("index.html", logged_in_user=user_dict)


@app.route("/twitter-pic/<screen_name>")
def twitter_pic(screen_name):
    url = redis_twitter_cache.get(screen_name)
    if url is None:
        url = api.get_user(screen_name=screen_name).profile_image_url
        redis_twitter_cache.setex(screen_name, url, 24 * 60 * 60)
    return redirect(url)


@app.route("/badge/<screen_name>")
def badge(screen_name):
    key = "%s:badge" % screen_name
    badge = redis_twitter_cache.get(key)
    if badge is None:
        try:
            score = tweet_resource.user_score_query(screen_name).get().score
            if score > 50000:
                badge = 5
            elif score > 10000:
                badge = 4
            elif score > 4000:
                badge = 3
            elif score > 500:
                badge = 2
            elif score > 0:
                badge = 1
            else:
                raise ValueError
            redis_twitter_cache.setex(key, badge, 60 * 60)

        except AttributeError:
            badge = 1

    return redirect(url_for("static", filename="img/badge-0%s.png" % badge))


@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = auth.authenticate(email, password)

    if not user:
        abort(401)

    auth.login_user(user)
    user_dict = user_resource.serialize_object(g.user)
    return jsonify(user_dict)


@app.route("/logout")
def logout():
    auth.logout_user(g.user)
    return redirect("/")
