import json,os
import threading
import Baadal
import MySQLdb as mdb
import ConfigParser
from userAuth import update_user_info
config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')

_authurl = config.get('auth', 'authurl')
_tenant = config.get('auth', 'tenant')

EXTERNAL_NETWORK = config.get('misc', 'external_network_name')

gateway_server = config.get('misc', 'gateway_server')
default_keypair = config.get('misc', 'default_keypair')


user_is_project_admin = False

response.delimiters = ('<?','?>')

if auth.is_logged_in():
    try:
        logger.debug("session is : " + str(session))
        logger.debug("user name in session is : " + str(session.username))
        new_db=mdb.connect("10.237.22.50","root","baadal","baadal")
        n_db=new_db.cursor()
        n_db.execute("select user_id,password from auth_user where username= %s",session.auth.user.username)
        data=n_db.fetchall()
        logger.debug("data value is : " +str(data))
        if len(data[0][0])== 0:
            logger.debug("inside if part ")
            my_user=data
            f = os.popen('openssl rand -hex 10')
            token = f.read()
            token = token.split("\n")
            token=token[0]
            logger.debug("token is : " + str(token))
            conn = Baadal.Connection(_authurl, _tenant,'e7221625e0c04660b22179605e8f6c52','baadal')
            my_user = conn.users_create(session.auth.user.username,token,_tenant)
            logger.debug("my user is : " + str(my_user))
            update_user_info(session.auth.user.username,my_user,token)
            value = conn.add_user_role(my_user, _tenant, 'user')
            logger.debug("add user role in openstack :  " + str(value) )
        else:
            my_user=data[0][0]
            token=data[0][1]
        logger.debug("my user is : " + str(my_user))         
        conn = Baadal.Connection(_authurl, _tenant, my_user, token)
        user_is_project_admin = conn.user_is_project_admin
    except Exception as e:
       logger.exception(e.message + str(e.__class__))
       logger.error('cannot determine if user is admin')
       raise HTTP(500)

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
    return "%i:%i:%i %i/%i/%i" % (t.tm_hour, t.tm_min, t.tm_sec, t.tm_mday, t.tm_mon, t.tm_year)


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
        self.retval = self._target(*self._args)
