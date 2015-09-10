import json
def new_vm():
    try:
        db.vm_requests.insert(
            vm_name = request.vars.vm_name,
            flavor = request.vars.config,
            sec_domain = request.vars.sec_domain,
            image = request.vars.template,
            owner = 'test'        )
        return json.dumps({'status':'success'})
    except Exception as e:
        return json.dumps({'status' : 'fail', 'message':e.message})
