
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

def networks():
    #conn = Baadal.Connection(authurl, tenant, username, password)
    if conn:
        networks = conn.networks()
        values = []
        for i in networks:
            if i.label != EXTERNAL_NETWORK:
                values.append({'name':i.label, 'id' : i.id})
        return json.dumps(values)

def sgroups():
    #conn = Baadal.Connection(authurl, tenant, username, password)
    if conn:
        sgroups = conn.sgroups()
        values = []
        for i in sgroups['security_groups']:
            values.append({'name':i['name'], 'id' : i['id']})
        return json.dumps(values)
