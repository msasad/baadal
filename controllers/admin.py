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
    action = request.vars.action
    if action == 'approve':
        try:
            row = db(db.vm_requests.id == request.vars.id).select()[0]
            vm = conn.createBaadalVM(row.name, row.image, row.flavor)
            if vm:
                return json.dumps({'status':'OK'})
        except Exception as e:
            return json.dumps({'status': 'fail','message':e.message})
        #vm = conn.createBaadalVM()
    return json.dumps({'message':'Request id %s is %s'%(request.vars.id,status[request.vars.action])})