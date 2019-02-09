#!/usr/bin/env python
import os
import re
import flask
import sys
import json
import pprint
from pymongo import MongoClient
import arrow
import pymongo
from datetime import timedelta
import datetime
from functools import wraps
from urllib2 import Request, urlopen, URLError
from flask import Flask, request, render_template, jsonify
from flask import url_for, abort, redirect, session
from utils import execute_action, agent_call, get_records
from utils import get_records_2, get_all_zones, get_all_zones_2, make_rnd_str, record_format
from utils import MasterConnectionFail, SlaveConnectionFail
from mavapa import mavapa, get_user_data
from bson.objectid import ObjectId
from datetime import datetime
from IPy import IP

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(os.environ['APP_SETTINGS'])
app.debug = app.config['DEBUG']
app.register_blueprint(mavapa, url_prefix='/mavapa')
app.secret_key = app.config['SECRET_KEY']

mongo_uri = 'mongodb://%s:%s@%s/%s' % (app.config['MONGO_USER'], app.config['MONGO_PASSWORD'], app.config['MONGO_HOST'], app.config['MONGO_DB'])
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client[app.config['MONGO_DB']]

if not app.config.has_key('CDN_LOCAL'):
    app.config['CDN_LOCAL'] = '%s/static' %app.config.get('APPLICATION_ROOT', '')

    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user', None)
        if user is None:
            return redirect(url_for('mavapa.login'))
        if 'active' not in user or not user['active']:
            return redirect(url_for('inactive'))
        return f(*args, **kwargs)
    return decorated_function


def expirations_privs(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        d = mongo_db.users.find_one({'id': session['user']['id']})
        if ('admin' in d and d['admin']) or ('expirations' in d and d['expirations']):
            return f(*args, **kwargs)
        return abort(403)
    return decorated_function


def admin_privs(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        d = mongo_db.users.find_one({'id': session['user']['id']})
        if not d or not d['admin']:
            del d['_id']
            session['user'] = d
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def delete_user_cache(user):
    cache_query = {'user': str(user['id'])}
    mongo_db.cache.delete_many(cache_query)


def update_user():
    mavapa_user = get_user_data(session)
    if isinstance(mavapa_user, str) or isinstance(mavapa_user, unicode):
        mavapa_user = json.loads(mavapa_user)
    if not mavapa_user:
        return None

    session['user'] = mavapa_user
    d = mongo_db.users.find_one({'id': session['user']['id']})
    if not d:
        doc = session['user']
        doc['admin'] = False
        doc['active'] = False
        doc['zones'] = []
        mongo_db.users.save(doc)
        session['user'] = doc
    else:
        save = False
        for key in session['user']:
            if key not in d or d[key] != session['user'][key]:
                d[key] = session['user'][key]
                save = True
        if 'admin' not in d:
            d['admin'] = False
            session['user']['admin'] = False
            save = True
        if 'active' not in d:
            d['active'] = False
            save = True
        if save:
            mongo_db.users.save(d)    
        session['user'] = d
    if '_id' in session['user']:
        session['user']['_id'] = str(session['user']['_id'])
    return True


def expiration_parser(e, today):
    days = (e['expiration'] - today).days
    if days <= 0:
        e['level'] = 'danger'
    elif days <= 30:
        e['level'] = 'warning'
    else:
        e['level'] = 'info'
    e['expiration_human'] = arrow.get(e['expiration']).humanize()
    return e


def parse_json(d):
    out = '#' * 80
    out = 'Json: \n'
    for key in d: 
        out += '%s: %s \n' % (key, d[key])
    out += '#' * 80
    return out


def parse_mx_record(data):
    if data['zone'] not in data['value']:
        if not data['value'].endswith('.'):
            data['value'] += '.'
        if '@' == data['name']:
            data['name'] = ''
        data['value'] += data['zone']
    return data


def parse_txt(data):
    if '@' in data['name']:
        data['name'] = ''
    if not data['value'].endswith('"'):
        data['value'] = '"%s"' % data['value']
    data['value'] = data['value'].replace('\\u2013', '-')
    return data


def parse_dname(data):
    data['name'] = '' 
    return data


@app.before_request
def before():
    refresh_user = False
    if 'last_update' not in session:
        session['last_update'] = datetime.now()
        refresh_user = True
    else:
        if (datetime.now() - session['last_update']).seconds > 60:
            refresh_user = True
            session['last_update'] = datetime.now()
    if 'user' in session and refresh_user:
        if update_user() is None:
            return redirect(url_for('mavapa.logout'))


@app.route('/')
@login_required
def index():
    zone = request.args.get('zone', None)
    ctx = {'app_name': 'dashboard'}
    query = {"expiration": {'$exists':1}}
    exp_counter = mongo_db.zones.find(query).count()
    query = {"expiration": {'$exists':0}}
    no_exp_counter = mongo_db.zones.find(query).count()
    ctx['exp_counter'] = exp_counter
    ctx['no_exp_counter'] = no_exp_counter
    p = []
    for i in mongo_db.zones.find().sort([('published', pymongo.DESCENDING)]).limit(5):
        p.append((i['zone'], i['published']))
    ctx['published'] = p

    return render_template('dashboard.html', ctx=ctx)

        
@app.route('/fresh_u/')
def fresh_user():
    update_user()
    return redirect(url_for('inactive'))


@app.route('/logout')
def logout():
    return redirect(url_for('mavapa.logout'))


@app.route('/admin/users/')
@login_required
def admin():
    if 'admin' in session['user'] and session['user']['admin']:
        users = mongo_db.users.find()
    else:
        users = mongo_db.users.find({'admin': False})  
    ctx = {'app_name': 'admin'}
    users = list(users)
    ctx['users'] = users
    ctx['users_cn'] = len(users)
    return render_template('admin/index.html', ctx=ctx)


@app.route('/inactive/')
def inactive():
    update_user()
    if not session['user'].get('active', False):
        return render_template('inactive.html', ctx={})
    else:
        return redirect(url_for('index'))    


@app.route('/admin/agents', methods=['GET', 'POST'])
@login_required
@admin_privs
def admin_agents():
    if request.method == 'POST':
        data = [(key, request.form.get(key).strip()) for key in request.form.keys()]
        data = dict(data)
        d = mongo_db.dns_servers.find_one({'ip': data['ip']})
        if not d:
            mongo_db.dns_servers.save(data)
    dnss = mongo_db.dns_servers.find().sort('type')
    agents = []
    master_zones = []
    master_exists = False
    for dns in dnss:
        try:
            data = agent_call(dns['path'], dns['secret_key'], {'request': 'show_zones'})
            zones = [d['zone'] for d in data['data']['zones']]
            dns['zones'] = zones
            if dns['type'] == 'Master':
                master_zones = set(dns['zones'])
                dns['zones_len'] = len(list(master_zones))
                master_exists = True
            else:
                dns['zones_diff'] = list(master_zones - set(dns['zones']))
                dns['zones_len'] = len(list(set(dns['zones'])))
                dns['zones_diff_len'] = len(dns['zones_diff'] )            
            dns['working'] = True
        except:
            dns['working'] = False
        agents.append(dns)
    ctx = {'app_name': 'dns_servers', 'dnss': agents, 'master_exists': master_exists}
    return render_template('admin/agents.html', ctx=ctx)


@app.route('/admin/agents/sync', methods=['GET'])
@login_required
@admin_privs
def admin_agents_sync():
    _id = request.args.get('id', False)
    if not _id:
        return 'false'
    master = mongo_db.dns_servers.find_one({'type': 'Master'})
    slave = mongo_db.dns_servers.find_one({'_id': ObjectId(_id)})
    data = agent_call(master['path'], master['secret_key'], {'request': 'show_zones'})
    master_zones = [(d['zone'], d['view']) for d in data['data']['zones']]
    data = agent_call(slave['path'], slave['secret_key'], {'request': 'show_zones'})
    slave_zones = [(d['zone'], d['view']) for d in data['data']['zones']]
    zones = set(master_zones) - set(slave_zones)
    action = {'request': 'add_zone'}
    action['master_host'] = master['ip']
    action['master'] = False
    for zone in zones:
        action['zone'] = zone[0]
        action['view'] = zone[1]
        data = agent_call(slave['path'], slave['secret_key'], action)
    return redirect(url_for('admin_agents'))


@app.route('/admin/ddns', methods=['GET', 'POST'])
@login_required
@admin_privs
def admin_ddns():
    if request.method == 'POST':
        ddns = request.form.get('ddns', False)
        doc = mongo_db.ddns.find_one({'ddns': ddns})
        if not doc:
            record = ddns.split('.', 1)[0]
            zone = ddns.split('.', 1)[1]
            doc = {'ddns': ddns, 'user': session['user']['id']}
            if 'displayname' in session['user']:
                doc['user_name'] = session['user']['displayname']
            doc['user_email'] = session['user']['email']
            doc['zone'] = zone
            doc['record'] = record
            doc['hash'] = make_rnd_str(20)
            mongo_db.ddns.save(doc)
            data = {'request': 'update_zone', 'action': 'add'}
            data['ttl'] = 300
            data['name'] = record
            data['value'] = '127.0.0.1'
            data['type'] = 'A'
            data['zone'] = zone
            execute_action(mongo_db, data, only_master=True)
    ddns = mongo_db.ddns.find()
    ctx = {'app_name': 'ddns_admin', 'ddns': ddns}
    return render_template('admin/ddns.html', ctx=ctx)


@app.route('/admin/edit_user/')
@login_required
def edit_user():
    user_id = request.args.get('user_id', None)
    if user_id:
        user = mongo_db.users.find_one({'id': user_id})
        if user:
            data = get_all_zones(mongo_db, session, no_records=True)
            z = data['data']['zones']
            d = dict([(d['zone'], d) for d in z])
            zones = []
            for k in z:
                k['name'] = k['zone']
            if 'admin' in session['user'] and not session['user']['admin']:
                for k in session['user']['zones']:
                    if k['admin']:
                        if k['name'] in d:
                            zones.append(d[k['name']])
            elif 'admin' in session['user'] and session['user']['admin']:
                zones = z
            ctx={'user': user, 'zones': zones, 'app_name': 'admin'} 
            return render_template('admin/edit_user.html', ctx=ctx)
    return redirect(url_for('admin'))


@app.route('/server_error')
@login_required
def server_error():
    return render_template('server_error.html', ctx={})


@app.route('/zone/expiration/edit/', methods=['GET', 'POST'])
def zone_expiration():
    zone = request.args.get('zone', False)
    ctx = {}
    if zone:
        zone = mongo_db.zones.find_one({'zone': zone})
        if zone:
            if request.method == 'POST':
                zone['owner'] = request.form.get('owner')
                zone['owner_mail'] = request.form.get('mail')
                zone['account'] = request.form.get('account', '')
                zone['comments'] = request.form.get('comments', '')
                expiration = request.form.get('expiration')
                zone['expiration'] = datetime.strptime(expiration, '%d/%m/%Y')
                mongo_db.zones.save(zone)
            if 'expiration' in zone and zone['expiration']:
                zone['expiration'] = zone['expiration'].strftime('%d/%m/%Y')
            ctx['zone'] = zone
    ctx['app_name'] = 'zone_expiration'
    return render_template('zone_expiration.html', ctx=ctx)


@app.route('/zone/expirations/')
@login_required
def expirations_list():
    expirations = []
    today = datetime.now() 
    last_days = today + datetime.timedelta(days=45)
    query = {"expiration": {'$exists':1}, "expiration": {"$lt": last_days}}
    for e in mongo_db.zones.find(query).sort([('expiration', pymongo.ASCENDING)]):
        e = expiration_parser(e, today)
        expirations.append(e)

    query = {"expiration": {'$exists':0}}
    for e in mongo_db.zones.find(query):

        expirations.append(e)

    ctx = {'expirations': expirations, 'app_name': 'expirations_list'}
    return render_template('expirations/index.html', ctx=ctx)


@app.route('/zone/expirations/search/')
@login_required
@expirations_privs
def expiration_search():
    search_by = request.args.get('search_by', None)
    ctx = {}
    if search_by:
        zone = mongo_db.zones.find_one({'zone': search_by})
        if 'expiration' in zone:
            zone['expiration'] = zone['expiration'].strftime('%d/%m/%Y')
        ctx['zone'] = zone
    zones = []
    for z in mongo_db.zones.find():
        zones.append({'name': z['zone']})
    ctx['zones'] = zones
    ctx['app_name'] = 'expirations_list'
    return render_template('expirations/search.html', ctx=ctx)


@app.route('/zone/publish_this/')
@login_required
def publish_this():
    pid = request.args.get('id', None)
    if pid:
        d = mongo_db.to_publish.find_one({'_id': ObjectId(pid)})
        if d:
            if session['user']['admin'] or d['user_id'] == session['user']['id']:
                d['action_logs'] = []
                for action in d['actions']:
                    out = execute_action(mongo_db, action, only_master=True)
                    pprint.pprint(out)
                    d['action_logs'].append(out)
                d['published'] = True
                d['published_datetime'] = datetime.now()
                username = session['user']['email']
                if 'displayname' in session['user'] and session['user']['displayname']:
                    username = session['user']['displayname']
                d['published_by'] = username
                mongo_db.to_publish.save(d)
                r = mongo_db.zones.find_one({'zone': d['zone']})
                docs = mongo_db.to_publish.find({'zone': r['zone'], 'published': True})
                if docs:
                    r['published'] = docs.count()
                    mongo_db.zones.save(r)
            cache_query = {'app': 'get_all_zones'}
            mongo_db.cache.delete_many(cache_query)
    return 'ok'


@app.route('/zone/publish_remove/')
@login_required
def publish_remove():
    pid = request.args.get('id', None)
    if pid:
        d = mongo_db.to_publish.find_one({'_id': ObjectId(pid)})
        d['published'] = 'True'
        d['deleted'] = 'True'
        username = session['user']['email']
        if 'displayname' in session['user'] and session['user']['displayname']:
            username = session['user']['displayname']
        d['published_by'] = username
        mongo_db.to_publish.save(d)
    return 'ok'


@app.route('/api/publish')
@login_required
def api_publish():
    zone = request.args.get('zone')
    status = request.args.get('status')
    data = []
    query = {}
    if status:
        query['published'] = True if status not in ['no', 'false', 'f'] else False
    if not session['user']['admin']:
        query['user_id'] = session['user']['id']
    if zone:
        query['zone'] = zone
    docs = list(mongo_db.to_publish.find(query).sort([('published_datetime', pymongo.ASCENDING)]))
    for d in docs:
        d['_id'] = str(d['_id'])
        d['out'] = ''
        if 'action_logs' in d:
            for cn, s in enumerate(d['action_logs']):
                d['out'] += parse_json(d['actions'][cn]) + '\n'
                if 'status' in s:
                    s['status'] = s['status'].replace('\n\n', '\n')
                    s['status'] = s['status'].replace('\n\n', '\n')
                    d['out'] += s['status']        
        data.append(d)
    return jsonify(datetime=datetime.now(), data=data)


@app.route('/unpublished')
@login_required
def unpublished():
    return render_template('unpublished/index.html', ctx={'app_name': 'to_publish'}) 


@app.route('/history')
@login_required
def history():
    return render_template('history/index.html', ctx={'app_name': 'Published'})


@app.route('/zones/')
@login_required
def zones_list():
    zone = request.args.get('zone', None)
    ctx = {'app_name': 'index'}
    if zone:
        r = False
        if session['user']['admin']:
            r = True
        else:
            for i in session['user']['zones']:
                if i['name'] == zone:
                    r = True
        if r:
            ctx['zone'] = zone
        else:
           return redirect(url_for('index')) 
    return render_template('zones/index.html', ctx=ctx)


@app.route('/zones/<zone>')
@login_required
def zone_page(zone) :
    view = request.args.get('view', 'private')
    ctx = {'app_name': 'index', 'view': view }
    if zone:
        r = False
        if session['user']['admin']:
            r = True
        else:
            for i in session['user']['zones']:
                if i['name'] == zone:
                    r = True
        if r:
            ctx['zone'] = zone
        else:
           return redirect(url_for('index')) 
    return render_template('zones/zone.html', ctx=ctx)


@app.route('/advanced_search/')
@login_required
def advanced_search():
    search_by = request.args.get('search_by', None)
    ctx = {'app_name': 'search'}
    if search_by:
        output = []
        search_by = search_by.strip()
        data = get_all_zones(mongo_db, session)
        zones = data['data']['zones']
        for zone in zones:
            if search_by in zone['zone']:
                for record in zone['records']:
                    if record['name'] == '@':
                        continue
                    output.append(record_format(zone['zone'], record))
                continue
            for record in zone['records']:
                if record['name'] == '@':
                    continue
                for k in record.keys():
                    if search_by in record[k]:
                        output.append(record_format(zone['zone'], record))
        if output:
            ctx['found'] = output
            ctx['search'] = search_by
    return render_template('search/advanced_search.html', ctx=ctx)


@app.route('/bulk_edit/', methods=['GET', 'POST'])
@login_required
def bulk_edit():
    ctx = {'app_name': 'search'}
    if request.method == 'POST':
        ctx['records'] = request.form['data']
    return render_template('search/bulk_edit.html', ctx=ctx)


@app.route('/api/logged_in/')
def logged_in():
    user = session.get('user', None)
    if user is None:
        abort(403)
    return 'ok'


@app.route('/api/admin/dns_servers/delete/')
@login_required
@admin_privs
def delete_dns():
    _id = request.args.get('id', False)
    doc = mongo_db.dns_servers.find_one({'_id': ObjectId(_id)})
    if doc:
        mongo_db.dns_servers.remove(doc)
    return 'ok'


@app.route('/api/admin/ddns/delete/')
@login_required
@admin_privs
def delete_ddns():
    _id = request.args.get('id', False)
    doc = mongo_db.ddns.find_one({'_id': ObjectId(_id)})
    if doc:
        if session['user']['admin'] or session['user']['id'] == doc['user']:

            soa, data = get_records(mongo_db, doc['zone'], no_parse=True)
            for r in data:
                if r['name'] == doc['name']:
                    zone = doc.get('zone')
                    data = {
                        'request': 'update_zone', 'action': 'del', 'zone': zone,
                        'ttl': r.get('ttl'), 'name': doc.get('name'),
                        'value': r.get('value'), 'type': r.get('type')
                    }
                    execute_action(mongo_db, data, only_master=True)
            mongo_db.ddns.remove(doc)
    return 'ok'


@app.route('/api/admin/ddns/update/')
def ddns_update():
    ddns_hash = request.args.get('hash', False)
    ip = request.args.get('ip', False)
    doc = mongo_db.ddns.find_one({'hash': ddns_hash})
    try:
        IP(ip)
    except ValueError:
        ip = False
    if doc and ip:
        if 'last_update' in doc:
            if (datetime.now() - doc['last_update']).seconds < 120:
                return 'requests exceeded'
        soa, rdata = get_records(mongo_db, doc['zone'], no_parse=True)
        exists = False
        for r in rdata:
            if r['name'] == doc['name']:
                actions = []
                zone = doc.get('zone')
                data = {'request': 'update_zone', 'action': 'del', 'zone': zone}
                data['ttl'] = r.get('ttl')
                data['name'] = doc.get('name')
                data['value'] = r.get('value')
                data['type'] = r.get('type')
                actions.append(data)
                data = {'request': 'update_zone', 'action': 'add', 'zone': zone}
                data['ttl'] = r.get('ttl')
                data['name'] = r.get('name')
                data['value'] = ip
                data['type'] = r.get('type')
                actions.append(data)
                for action in actions:
                    execute_action(mongo_db, action, only_master=True)
                doc['last_update'] = datetime.now()
                doc['ip'] = ip
                mongo_db.ddns.save(doc)
                exists = True
                break
        if not exists:
            actions = []
            data = {'request': 'update_zone', 'action': 'add', 'zone': doc['zone']}
            data['ttl'] = '300'
            data['name'] = doc['name']
            data['value'] = ip
            data['type'] = 'A'
            data['view'] = 'private'
            actions.append(data)
            for action in actions:
                execute_action(mongo_db, action, only_master=True)
            doc['last_update'] = datetime.now()
            doc['ip'] = ip
            mongo_db.ddns.save(doc)

    return 'ok'


@app.route('/api/admin/change_privs/')
@login_required
@admin_privs
def change_privs():
    user_id = request.args.get('user_id', None)  
    if user_id:
        user = mongo_db.users.find_one({'id': user_id})
        if user:
            if 'admin' not in user:
                user['admin'] = False
            if 'zones' not in user:
                user['zones'] = []
            user['admin'] = False if user['admin'] else True
            mongo_db.users.save(user)
            delete_user_cache(user)
    return 'ok'


@app.route('/api/admin/change_status/')
@login_required
@admin_privs
def change_status():
    user_id = request.args.get('user_id', None)  
    if user_id:
        user = mongo_db.users.find_one({'id': user_id})
        if user:
            if 'active' not in user:
                user['active'] = False
            user['active'] = False if user['active'] else True
            mongo_db.users.save(user)
            delete_user_cache(user)
    return 'ok'


@app.route('/api/admin/change_expirations/')
@login_required
@admin_privs
def change_expirations():
    user_id = request.args.get('user_id', None)  
    if user_id:
        user = mongo_db.users.find_one({'id': user_id})
        if user:
            if 'expirations' not in user:
                user['expirations'] = False
            user['expirations'] = False if user['expirations'] else True
            mongo_db.users.save(user)
            delete_user_cache(user)
    return 'ok'


@app.route('/api/admin/change_user_zone_privs/')
@login_required
@admin_privs
def change_user_zone_privs():
    user_id = request.args.get('user_id', None)  
    zone = request.args.get('zone', None) 
    if user_id and zone:
        user = mongo_db.users.find_one({'id': user_id})
        if user:
            if 'zones' not in user:
                user['zones'] = []
            for cn, z in enumerate(user['zones']):
                if z['name'] == zone:
                    if 'admin' not in z:
                        z['admin'] = True
                    else:
                        z['admin'] = False if z['admin'] else True
                    mongo_db.users.save(user)
            delete_user_cache(user)
    return 'ok'


@app.route('/api/admin/edit_user_zones/')
@login_required
@admin_privs
def edit_user_zones():
    user_id = request.args.get('user_id', None)  
    zone = request.args.get('zone', None) 
    action = request.args.get('action', None) 
    admin = request.args.get('admin', False) 
    if user_id and zone:
        user = mongo_db.users.find_one({'id': user_id})
        if user:
            if 'zones' not in user:
                user['zones'] = []
            if action == 'add':
                if zone not in [x['name'] for x in user['zones']]:
                    user['zones'].append({'name': zone, 'admin': admin})
                    mongo_db.users.save(user)
            elif action == 'del':
                for cn, z in enumerate(user['zones']):
                    if z['name'] == zone:
                        del user['zones'][cn]
                        mongo_db.users.save(user)
                        break
            delete_user_cache(user)
    return 'ok'


@app.route('/api/bulk_save/', methods=['GET', 'POST'])
@login_required
def bulk_save():
    ctx = {}
    if request.method == 'POST':
        data = json.loads(request.form['data'])
        actions = data['actions']
        note = data['note']
        bulk_actions = []
        for a in actions:
            data = {'request': 'update_zone', 'action': 'del', 'zone': a['original']['zone']}
            data['ttl'] = a['original']['ttl']
            data['name'] = a['original']['name']
            data['value'] = a['original']['value']
            data['type'] = a['original']['type']
            bulk_actions.append(data)
            data = {'request': 'update_zone', 'action': 'add', 'zone': a['new']['zone']}
            data['ttl'] = a['new']['ttl']
            data['name'] = a['new']['name']
            data['value'] = a['new']['value']
            data['type'] = a['new']['type']
            bulk_actions.append(data)
        doc = {'zone': 'BULK', 'actions': bulk_actions}
        doc['name'] = 'BULK'
        doc['note'] = note
        doc['action'] = 'Edit'
        doc['user_id'] = session['user']['id']
        doc['user'] = session['user']
        doc['published'] = False
        mongo_db['to_publish'].save(doc)
    return 'ok'


@app.route('/api/v2/zones')
def api_zones():
    zone = request.args.get('zone', None)
    view = request.args.get('view', None)    
    data = {'request': 'show_zones'}
    if zone:
        soa, records = get_records_2(mongo_db, {'zone': zone, 'view': view})
        records = sorted(records, key=lambda k: k['type'])
        data = {'records': records}
        if not session['user']['admin']:
            docs = mongo_db.to_publish.find({
                'zone': zone, 'user_id': session['user']['id'], 'published': False
            })
        else:
            docs = mongo_db.to_publish.find({'zone': zone, 'published': False})
        data['to_publish'] = docs.count()
    else:
        try:
            data = get_all_zones_2(mongo_db, session, app=app)
        except Exception as e:
            print e
    return jsonify(data)
    

@app.route('/api/zones/')
def show_zones():
    if 'user' not in session:
        return abort(403)
    zone = request.args.get('zone', None)
    data = {'request': 'show_zones'}
    if zone:
        soa, records = get_records(mongo_db, zone)
        records = sorted(records, key=lambda k: k['type'])
        data = {'records': records}
        if not session['user']['admin']:
            docs = mongo_db.to_publish.find({
                'zone': zone, 'user_id': session['user']['id'], 'published': False
            })
        else:
            docs = mongo_db.to_publish.find({'zone': zone, 'published': False})
        data['to_publish'] = docs.count()
    else:
        try:
            data = get_all_zones(mongo_db, session, app=app)
        except Exception as e:
            print e
    return jsonify(data)


@app.route('/api/zones/add_zone/', methods=['GET', 'POST'])
@login_required
def add_zone():
    data = {'request': 'add_zone'}
    data['zone'] = request.args.get('zone_name', None)
    data['view'] = request.args.get('view', None)
    data['master'] = True
    doc = mongo_db.dns_servers.find_one({'type': 'Master'})
    data['master_host'] = doc['ip']
    execute_action(mongo_db, data, only_master=True)
    data['master'] = False
    execute_action(mongo_db, data, only_slaves=True)
    cache_query = {'app': 'get_all_zones'}
    mongo_db.cache.delete_many(cache_query)
    return jsonify(data)


@app.route('/api/zones/del_zone/', methods=['GET', 'POST'])
@login_required
@admin_privs
def remove_zone():
    data = {'request': 'del_zone'}
    zone = request.args.get('zone', None)
    data['zone'] = zone
    data['view'] = request.args.get('view', 'public')
    execute_action(mongo_db, data, only_slaves=True)
    execute_action(mongo_db, data, only_master=True)
    mongo_db.zones.delete_many({'zone': zone})
    cache_query = {'app': 'get_all_zones'}
    mongo_db.cache.delete_many(cache_query)
    return jsonify(data)


@app.route('/api/zones/record/add/', methods=['GET', 'POST'])
@login_required
def add_record():
    data = {'request': 'update_zone', 'action': 'add'}
    keys = ['ttl', 'name', 'value', 'type', 'zone', 'note', 'view']
    errors = {'errors': []}
    for k in keys:
        tmp = request.form.get(k, False)
        if tmp == False:
            error = (k, 'missing')
            errors['errors'].append(error)
        else:
            tmp = tmp.strip()
        data[k] = tmp
    if errors['errors']:
        r = jsonify(errors)
        r.status_code = 400
        return r
    print '#' * 80
    pprint.pprint(data)
    if data['type'] == 'MX':
        data = parse_mx_record(data)
    elif data['type'] == 'TXT':
        data = parse_txt(data)
    elif data['type'] == "DNAME":
        data = parse_dname(data)
    elif data['type'] == 'A':
        if data['zone'] in data['value']:
            data['value'] = data['value'].replace(data['zone'], '')
    if data['name'] == '.' or data['name'] == '@':
        data['name'] = ''
    pprint.pprint(data)
    zone = data['zone']
    #doc = mongo_db['to_publish'].find_one({'zone': zone})
    doc = {'zone': zone, 'actions': []}
    doc['actions'].append(data)
    doc['note'] = data['note']
    doc['name'] = data.get('name')
    doc['action'] = 'Add'
    doc['user_id'] = session['user']['id']
    doc['user'] = session['user']
    doc['published'] = False
    mongo_db['to_publish'].save(doc)
    return jsonify(data)


@app.route('/api/zones/record/edit/', methods=['GET', 'POST'])
@login_required
def edit_record():
    keys = ['ttl', 'name', 'value', 'type', 'zone', 'note', 'view']
    keys += ['ttl_original', 'name_original', 'value_original', 'type_original']
    errors = {'errors': []}

    for k in keys:
        tmp = request.values.get(k, False)
        if not tmp:
            error = (k, 'missing')
            errors['errors'].append(error)
            r = jsonify(errors)
            r.status_code = 400
            return r

    actions = []
    zone = request.args.get('zone')
    data = {'request': 'update_zone', 'action': 'del', 'zone': zone, 'view': request.args.get('view')}
    data['ttl'] = request.values.get('ttl_original')
    data['name'] = request.values.get('name_original')
    data['value'] = request.values.get('value_original')
    data['type'] = request.values.get('type_original')
    if data['type'] == 'MX':
        data = parse_mx_record(data)
    elif data['type'] == 'TXT':
        data = parse_txt(data)
        
    actions.append(data)
    data = {'request': 'update_zone', 'action': 'add', 'zone': zone, 'view': request.args.get('view')}
    data['ttl'] = request.args.get('ttl')
    data['name'] = request.args.get('name')
    data['value'] = request.args.get('value')
    data['type'] = request.args.get('type_original')
    if data['type'] == 'MX':
        data = parse_mx_record(data)

    actions.append(data)
    doc = {'zone': zone, 'actions': actions, 'view': request.args.get('view')}
    doc['name'] = request.args.get('name')
    doc['note'] = request.args.get('note')
    doc['action'] = 'Edit'
    doc['user_id'] = session['user']['id']
    doc['user'] = session['user']
    doc['published'] = False
    mongo_db['to_publish'].save(doc)
    return jsonify(data)


@app.route('/api/zones/record/remove/', methods=['GET', 'POST'])
@login_required
def remove_record():
    data = {'request': 'update_zone', 'action': 'del'}
    keys = ['ttl', 'name', 'value', 'type', 'zone', 'view']
    errors = {'errors': []}
    for k in keys:
        tmp = request.values.get(k)
        if not tmp:
            error = (k, 'missing')
            errors['errors'].append(error)
        data[k] = tmp
    if errors['errors']:
        r = jsonify(errors)
        r.status_code = 400
        return r

    if data['type'] == 'NS' and data['zone'] not in data['value']:
        data['value'] += '.' + data['zone']
    if data['type'] == 'CNAME':
        if data['value'] == '@':
            data['value'] = data['zone']
    if data['type'] == 'MX':
        data = parse_mx_record(data)

    elif data['type'] == 'TXT':
        data = parse_txt(data)
    print data
    zone = data['zone']
    #doc = mongo_db['to_publish'].find_one({'zone': zone})
    doc = {'zone': zone, 'actions': []}
    doc['actions'].append(data)
    doc['note'] = 'Removing record'
    doc['name'] = request.args.get('name')
    doc['action'] = 'Del'
    doc['user_id'] = session['user']['id']
    doc['user'] = session['user']
    doc['published'] = False
    mongo_db['to_publish'].save(doc)
    return jsonify(data)


if __name__ == "__main__":
    app.run('0.0.0.0', 7004)
