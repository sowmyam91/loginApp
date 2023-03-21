########################################################################################
######################          Import packages      ###################################
########################################################################################
from functools import wraps
from typing import Optional, Tuple

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import db
import json
import requests
from tools import decode_token
from sqlalchemy.orm.exc import NoResultFound

auth = Blueprint('auth', __name__)  # create a Blueprint object that we name 'auth'
from app_config import var


def require_api_token(func):
    @wraps(func)
    def check_token(*args, **kwargs):
        # Check to see if it's in their session
        if 'sub' not in session:
            # If it isn't return our access denied message (you can also return a redirect or render_template)
            return redirect(url_for('main.index'))

        # Otherwise just send them where they wanted to go
        return func(*args, **kwargs)

    return check_token


@auth.route('/login', methods=['GET', 'POST'])  # define login page path
def login():  # define login page fucntion
    if request.method == 'GET':  # if the request is a GET we return the login page
        url = var.get('base_url') + var.get('authorize') + "?"
        for key in var["params"].keys():
            if key not in ("client_secret", "grant_type"):
                url = url + "&" + key + "=" + var["params"].get(key)
        return redirect(url, code=302)
    else:
        return {"error": "Method not implemented", "code": "501"}

@auth.route('/signup', methods=['GET', 'POST'])  # we define the sign up path
def signup():  # define the sign up function
    if request.method == 'GET':  # if the request is a GET we return the login page
        return redirect(
            "https://v1.api.us.janrain.com/00000000-0000-0000-0000-000000000000/login/authorize?client_id=363bc604-f69a-42dd-b7de-6fa05e1f1478&redirect_uri=http://localhost:5000/identity/callback&response_type=code&scope=openid+profile+email&state=zrJTlylQDmDhgJH6sB4FDCWm8l3evGoKuMat4USxpUQ&nonce=12345&prompt=create",
            code=302)


@auth.route('/logout')  # define logout path
@login_required
def logout():  # define the logout function
    session.pop('sub', default=None)
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/user')  # define logout path
@login_required
def user():  # define the logout function
    params = var.get('params')
    profile = var.get('base_url')+var.get("profile") + "?redirect_uri=" + params.get("redirect_uri")+"&client_id="+params.get('client_id')
    return redirect(profile)


@auth.route('/identity/callback', methods=['GET'])  # define login page path
def callbak():  # define login page function
    access_code = request.args.get('code')
    if access_code:

        user: dict = exchange_code_for_token(access_code)

        # Create session
        query = User.query.filter_by(user_id=user.get('sub'))

        try:
            user = query.one()
        except NoResultFound:
            user = User(user_id=user.get('sub'), email=user.get('email'), name=user.get('name'))
            db.session.add(user)
            db.session.commit()
        login_user(user, remember=True)
        session['sub'] = user.get('sub')
        return redirect(url_for('main.profile'))
    else:
        return redirect(url_for('main.index'))


def exchange_code_for_token(access_code):
    url = var.get("token_url")
    params = var.get("params")
    payload = "grant_type=" + params.get('grant_type') + "&client_id=" + params.get(
        'client_id') + "&redirect_uri=" + params.get(
        'redirect_uri') + "&code=" + access_code + "&client_secret=" + params.get('client_secret')
    payload = 'grant_type=authorization_code&client_id=363bc604-f69a-42dd-b7de-6fa05e1f1478&redirect_uri=http://localhost:5000/identity/callback&code=' + access_code + '&client_secret=97DZ21KZskNyT7r9lM-M45rGcnBKvivwZT2sqNbCzFeuZ2o6R-M1zwdaDtKQ4T9TiZgIBG0cEOhFht9J8CaoLQ'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    user_info = parse_id_token(response.json().get('id_token'))

    return user_info


def parse_id_token(token):
    user = {}
    if token:
        d_token: dict = json.loads(decode_token(token)[1])
        user['name'] = d_token.get('given_name')
        user['email'] = d_token.get('email')
        user['sub'] = d_token.get('sub')
        user['is_active'] = True

    else:
        print("ID token not found")
    return user
