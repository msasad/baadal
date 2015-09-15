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
            public_ip_required = 1 if request.vars.public_ip == 'yes' else 0,
            extra_storage = request.vars.storage,
            collaborators = request.vars.collaborators,
            request_time = int(time.time())
        )
        db.commit()
        return jsonify()
    except Exception as e:
        return jsonify(status='fail', message=str(e.__class__))

def modify_request():
    try:
        db(db.vm_requests.id == request.vars.id).update(
            extra_storage = request.vars.storage,
            public_ip_required = 1 if request.vars.public_ip == 'yes' else 0,
            flavor = request.vars.flavor)
        db.commit()
        return jsonify()
    except Exception as e:
        return jsonify(status=fail, message = str(e.__class__))