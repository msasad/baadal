import json
import threading


user_is_project_admin = False

try:
    conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
    user_is_project_admin = conn.user_is_project_admin
except Exception:
    pass
finally:
    try:
        conn.close()
    except NameError:
        pass

def jsonify(status='success', **kwargs):
    d = dict()
    d['status'] = status
    for i in kwargs:
        d[i] = kwargs[i]
    return json.dumps(d)


def seconds_to_localtime(seconds):
    import time
    t = time.localtime(seconds)
    return "%i:%i:%i %i/%i/%i"%(t.tm_hour, t.tm_min, t.tm_sec, t.tm_mday, t.tm_mon, t.tm_year)


def network_name_from_id(netid):
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        netlist = conn.networks()['networks']
        for i in netlist:
            if netid == i['id']:
                return i['name']
    except Exception:
        pass
    finally:
        conn.close()


def str_to_route_list(s):
    l = s.split('\r\n')
    route_list = []
    for i in l:
        temp = i.split(':')
        route_list.append({'destination': temp[0], 'nexthop': temp[1]})
    return route_list


def flavor_info(flavor_id):
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        flavor = conn.find_template(id=flavor_id)
        return str(flavor.vcpus) + (' VCPU, ' if flavor.vcpus == 1 else ' VCPUs, ') + str(flavor.ram) + ' MB RAM'
    except Exception:
        pass
    finally:
        conn.close()


def convert_timezone(utctimestring, fmt="%Y-%m-%dT%H:%M:%SZ", timezone='Asia/Kolkata'):
    from datetime import datetime
    import pytz
    utc_time = datetime.strptime(utctimestring, fmt)
    utc_time_withtz = utc_time.replace(tzinfo=pytz.utc)
    localtime = utc_time_withtz.astimezone(pytz.timezone(timezone))
    return localtime.strftime(fmt)

    
class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
 
    def run(self):
        self._target(*self._args)
