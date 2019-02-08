from donutslibs import crypt_request
import datetime
import dns.zone
import dns.query
import random
import string
import pprint


class MasterConnectionFail(Exception):
    pass

class SlaveConnectionFail(Exception):
    pass

def agent_call(path, secret_key, action):
    data = crypt_request(path, action, secret_key)
    return data

def execute_action(mongo_db, action, only_master=False, only_slaves=False, debug=False):

    data = []
    if only_master:
        try:
            print(action)
            doc = mongo_db.dns_servers.find_one({'type': 'Master'})
            data = agent_call(doc['path'], doc['secret_key'], action)
            doc['last_update'] = datetime.datetime.now()
            mongo_db.dns_servers.save(doc)
            if True:
                pprint.pprint(data)
        except Exception as e:
            raise MasterConnectionFail
    if only_slaves:
            for slave in mongo_db.dns_servers.find({'type': 'Slave'}):

                try:
                    data += [agent_call(slave['path'], slave['secret_key'], action)]
                except Exception as e:
                    continue
                slave['last_update'] = datetime.datetime.now()
                mongo_db.dns_servers.save(slave)
                if debug:
                    pprint.pprint(data)
    return data


def get_record(key, ovalues):
    record = {}
    values = ovalues.split(key)
    record_value = values[1]
    values = values[0].split()
    record['record_type'] = key
    record['record'] = values[0]
    record['ttl'] = values[1]
    record['record_value'] = record_value
    return record


def parse_record(zone, ovalues):
    if 'SOA' in ovalues:
        return None
    values = ovalues.split()
    record = {}
    if len(values) == 5:
        record['record'] = values[0]
        record['ttl'] = values[1]
        record['record_type'] = values[3]
        record['record_value'] = values[4]
    else:
        values = ovalues.split('"')
        if len(values) == 3:
            record_value = values[1]
            values = values[0].split()
            record['record'] = values[0]
            record['ttl'] = values[1]
            record['record_type'] = values[3]
            record['record_value'] = record_value
        else:
            found = False
            for key in ['SRV', 'MX', 'RSIG', 'TXT', 'DNSKEY', 'NSEC3PARAM', 'TYPE65534']:
                if key in ovalues:
                    record = get_record(key, ovalues)
                    found = True
                    break
    return record


def get_records(mongo_db, zone, no_parse=False, app=None):
    doc = mongo_db.dns_servers.find_one({'type': 'Master'})
    z = dns.zone.from_xfr(dns.query.xfr(doc['ip'], zone))
    names = z.nodes.keys()
    names.sort()
    records = []
    ddns = list(mongo_db.ddns.find({'zone': zone}))
    soa = {}
    for n in names:
        txt = z[n].to_text(n)
        for t in txt.split('\n'):
            if 'SOA' in t:
                soa['raw'] = t
                ts = t.split('.')[-1].strip().split()[0]
                soa['ts'] = ts
            r = parse_record(zone, t)
            if r:
                if not no_parse:
                    for d in ddns:
                        if r['record'] == d['record']:
                            r['record_type'] = 'DDNS'
                            r['record_value'] += " hash(%s)" % d['hash']
                records.append(r)
    return soa, records

    
def parse_zone(r, mongo_db, session, no_records, app):
    if not no_records:
        try:
            r['soa'], r['records'] = get_records(
                mongo_db, r['zone'], app=app
            )
        except dns.exception.FormError:
            data['data']['zones'].remove(r)
            return False
    doc = mongo_db.zones.find_one({'zone': r['zone']})
    r['name'] = r['zone']
    r['to_publish'] = 0
    if session['user']['admin']:
        docs = mongo_db.to_publish.find({'zone': r['zone'], 'published': False})
    else:
        docs = mongo_db.to_publish.find({'zone': r['zone'], 'user_id': session['user']['id'],
            'published': False})
    if docs:
        r['to_publish'] = docs.count()
    if 'records' not in r:
        r['records'] = []

    if doc and 'published' not in doc:
        r['published'] = mongo_db.to_publish.find({'zone': r['zone'], 'published': True}).count()
    else:
        r['published'] = mongo_db.to_publish.find({'zone': r['zone'], 'published': True}).count()
    if doc:
        save = False
        for key in r:
            if key not in doc or r[key] != doc[key]:
                doc[key] = r[key]
                save = True
        if save:
            mongo_db.zones.save(doc)
    else:
        mongo_db.zones.save(r)
        r['_id'] = str(r['_id'])
    return r


def get_all_zones(mongo_db, session, no_records=False, debug=False, no_cache=False, app=None):
    user = session.get('user')
    uid = user.get('id')
    cache_query = {'app': 'get_all_zones', 'user': uid}
    doc = mongo_db.cache.find_one(cache_query)
    if doc:
        doc['data']['cached'] = True
        return doc['data']
    data = {'request': 'show_zones'}
    data = execute_action(mongo_db, data, only_master=True, debug=debug)
    print 'Print execute_action!'
    pprint.pprint(data)
    print
                  
    zones = []
    azones = None
    user = mongo_db.users.find_one({'email': session['user']['email']})
    print 'user'
    pprint.pprint(user)
    if not user['admin']:
        azones = [x['name'] for x in user['zones']]
    for r in data['data']['zones']:
        if azones is not None:
            if unicode(r['zone']) not in azones:
                continue
        r = parse_zone(r, mongo_db, session, no_records, app)
        if r:
            zones.append(r)
    data['data']['zones'] = zones
    data['data']['count'] = len(zones)
    cache_query['data'] = data
    cache_query['last_update'] = datetime.datetime.now()
    mongo_db.cache.save(cache_query)
    data['data']['cached'] = False
    print 'data'
    pprint.pprint(data)
    return data

def get_records_2(mongo_db, zone, no_parse=False, app=None, debug=False):
    doc = mongo_db.dns_servers.find_one({'type': 'Master'})
    data = { 'request': 'zone.get', 'zone': zone.get('zone'), 'view': zone.get('view') }
    # z = dns.zone.from_xfr(dns.query.xfr(doc['ip'], zone))
    res = execute_action(mongo_db, data, only_master=True, debug=debug)
    print(res)
    soa = res['data'][0]
    records = res['data'][1]
    return soa, records

def parse_zone_2(r, mongo_db, session, no_records, app):
    if not no_records:
        try:
            r['soa'], r['records'] = get_records_2(
                mongo_db, r, app=app
            )
        except dns.exception.FormError:
            data['data']['zones'].remove(r)
            return False
    doc = mongo_db.zones.find_one({'zone': r['zone']})
    r['name'] = r['zone']
    r['to_publish'] = 0
    if session['user']['admin']:
        docs = mongo_db.to_publish.find({'zone': r['zone'], 'published': False})
    else:
        docs = mongo_db.to_publish.find({'zone': r['zone'], 'user_id': session['user']['id'],
            'published': False})
    if docs:
        r['to_publish'] = docs.count()
    if 'records' not in r:
        r['records'] = []

    if doc and 'published' not in doc:
        r['published'] = mongo_db.to_publish.find({'zone': r['zone'], 'published': True}).count()
    else:
        r['published'] = mongo_db.to_publish.find({'zone': r['zone'], 'published': True}).count()
    if doc:
        save = False
        for key in r:
            if key not in doc or r[key] != doc[key]:
                doc[key] = r[key]
                save = True
        if save:
            mongo_db.zones.save(doc)
    else:
        mongo_db.zones.save(r)
        r['_id'] = str(r['_id'])
    return r

def get_all_zones_2(mongo_db, session, no_records=False, debug=False, no_cache=False, app=None):
    user = session.get('user')
    uid = user.get('id')
    cache_query = {'app': 'get_all_zones', 'user': uid}
    doc = mongo_db.cache.find_one(cache_query)
    if doc:
        doc['data']['cached'] = True
        return doc['data']
    data = {'request': 'show_zones'}
    data = execute_action(mongo_db, data, only_master=True, debug=debug)
    print 'Print execute_action!'
    pprint.pprint(data)
    print
                  
    zones = []
    azones = None
    user = mongo_db.users.find_one({'email': session['user']['email']})
    print 'user'
    pprint.pprint(user)
    if not user['admin']:
        azones = [x['name'] for x in user['zones']]
    for r in data['data']['zones']:
        if azones is not None:
            if unicode(r['zone']) not in azones:
                continue
        print(r)
        r = parse_zone_2(r, mongo_db, session, no_records, app)
        if r:
            zones.append(r)
    data['data']['zones'] = zones
    data['data']['count'] = len(zones)
    cache_query['data'] = data
    cache_query['last_update'] = datetime.datetime.now()
    mongo_db.cache.save(cache_query)
    data['data']['cached'] = False
    print 'data'
    pprint.pprint(data)
    return data

def make_rnd_str(l=10):
    return ''.join([random.choice(string.letters+string.digits) for x in range(l)])

def record_format(zone, record):
    record['zone'] = zone
    return record
