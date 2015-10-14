"""import Baadal
import json
import ConfigParser
from gluon import *
# work around to stop stupid editors from complaining about undeclared 'request'
if False:
    request = dict()
    response = dict()
config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')
authurl = config.get('auth','authurl')
tenant = config.get('auth','tenant')
password = config.get('auth','password')
username = config.get('auth', 'username')"""

from gluon import *
def configs():
    #conn = Baadal.Connection(authurl, tenant, username, password)
    if conn:
        templates = conn.templates()
        values = []
        for t in templates:
            #Will need to change here if templates are wrapped in Baadal.Templates
            d = t.to_dict()
            values.append({'id':d['id'], 'ram':d['ram'], 'vcpus':d['vcpus']})
        return json.dumps(values)
            
def templates():
    #conn = Baadal.Connection(authurl, tenant, username, password)
    """The following metadata needs to be attached to each image
        os-name,
        os-version,
        os-arch,
        disk-size,
        os-edition, (desktop/server)
    """
    if conn:
        images = conn.images()
        values = []
        for i in images:
            #Will need to change here if images are wrapped in Baadal.Images
            m = i.to_dict()['metadata']
            m['id'] = i.id
            values.append(m)
        return json.dumps(values)

def sdomains():
    #conn = Baadal.Connection(authurl, tenant, username, password)
    if conn:
        domains = conn.networks()
        values = []
        for i in domains:
            values.append({'name':i.label, 'id' : i.id})
        return json.dumps(values)
