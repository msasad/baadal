from gluon import *
import json
def pending_requests():
    rows = db().select(db.vm_requests.ALL)
    return json.dumps({'data': rows.as_list()})
    pass

def pending_requests_list():
    return dict()