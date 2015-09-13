from gluon import *
import json
import Baadal
def pending_requests():
    rows = db().select(db.vm_requests.ALL)
    return json.dumps({'data': rows.as_list()})
    pass

def pending_requests_list():
    return dict()

def handle_request():
    status = {'edit':'edited','approve': 'approved', 'reject' : 'rejected'}
    rid = request.vars.id
    action = request.vars.request
    if action == 'approve':
        
    return json.dumps({'message':'Request id %s is %s'%(request.vars.id,status[request.vars.action])})