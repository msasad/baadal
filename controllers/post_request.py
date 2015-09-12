import json
from gluon import *
import time
def new_vm():
    try:
        db.vm_requests.insert(
            vm_name = request.vars.vm_name,
            flavor = request.vars.config,
            sec_domain = request.vars.sec_domain,
            image = request.vars.template,
            owner = 'test',
            purpose = request.vars.purpose,
            public_ip_required = 1 if request.vars.public_ip == 'Yes' else 0,
            extra_storage = request.vars.storage,
            collaborators = requests.vars.collaborators,
            request_time = int(time.time())
        )
        db.commit()
        return json.dumps({'status':'success'})
    except Exception as e:
        #response.status = '500'
        return json.dumps({'status' : 'fail', 'message': str(e.__class__)})