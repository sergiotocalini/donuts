from flask import Blueprint, render_template, abort, redirect, current_app, request, jsonify, session, url_for
from jinja2 import TemplateNotFound
import requests
import json

mavapa = Blueprint('mavapa', __name__, template_folder='templates')

@mavapa.route('/login/')
def login():
    url = current_app.config['MAVAPA_URL'] + '/auth?response_type=code'
    url += '&client_id=%s&redirect_uri=%s'
    url = url % (current_app.config['CLIENT_ID'],
                 current_app.config['REDIRECT_URI'])
    return redirect(url)

@mavapa.route('/logout/')
def logout():
    url = current_app.config['MAVAPA_URL'] + '/logout'
    session.pop('user', None)
    session.pop('access_token', None)
    return redirect(url)

@mavapa.route('/code/')
def mavapa_code():
    url_token = current_app.config['MAVAPA_URL'] + '/token'
    url_userinfo = current_app.config['MAVAPA_URL'] + '/who_im/'
    code = request.args.get('code')
    data = {'code': code}
    data['grant_type'] = 'authorization_code'
    data['redirect_uri'] = current_app.config['REDIRECT_URI']
    data['client_id'] = current_app.config['CLIENT_ID']
    data['client_secret'] = current_app.config['CLIENT_SECRET']
    r = requests.post(url_token, data=data, verify=False)
    data = json.loads(r.text)
    token = data['access_token']
    r = requests.get(url_userinfo + '?token=' + token, verify=False)
    data = json.loads(r.text)
    session['user'] = data
    session['access_token'] = token
    return redirect(url_for('fresh_user'))

def get_user_data(session):
    url = current_app.config['MAVAPA_URL'] + '/who_im/'
    r = requests.get(url + '?token=' + session['access_token'], verify=False)
    if r.status_code == 200:
        return r.text
    return False

@mavapa.route('/who_im/')
def who_im():
    data = get_user_data(session)
    if data:
        return jsonify(data)
    return 'fail'
