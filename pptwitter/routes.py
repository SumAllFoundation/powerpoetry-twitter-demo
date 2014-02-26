from flask import abort, g, jsonify, redirect, request, render_template

from .app import app

from .core.model import User
from .core.auth import auth
from .core.rest import api, UserResource


user_resource = UserResource(api, User, None, ["GET"])


@app.route("/")
def index():
    user_dict = None
    if g.user:
        user_dict = user_resource.serialize_object(g.user)
    return render_template("index.html", logged_in_user=user_dict)


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
