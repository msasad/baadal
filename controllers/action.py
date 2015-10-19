
from gluon import *
import json
# work around to stop stupid editors from complaining about undeclared 'request'
if False:
    request = dict()

def __do(action, vmid):
    #conn = Baadal.Connection("http://10.237.23.178:35357/v2.0", "admin", "admin", "baadal")
    if conn:
        vm = conn.findBaadalVM(id=request.vars.vmid)
        if vm:
            if action == 'start':
                vm.start()
            elif action == 'shutdown':
                vm.shutdown()
            elif action == 'pause':
                vm.pause()
            elif action == 'reboot':
                vm.reboot()
            elif action == 'delete':
                vm.delete()
            elif action == 'resume':
                vm.resume()

        conn.close()
        return jsonify()
    else:
        conn.close()
        return jsonify(status='failure')

def start():
    return __do('start', request.vars.vmid)
    
def shutdown():
    return __do('shutdown', request.vars.vmid)
    
def pause():
    return __do('pause', request.vars.vmid)
    
def reboot():
    return __do('reboot', request.vars.vmid)

def delete():
    return __do('delete', request.vars.vmid)

def resume():
    return __do('resume', request.vars.vmid)


def handle_request():
    action = request.vars.action
    if action == 'approve':
        return __create()
    elif action == 'edit':
        pass
    elif action == 'reject':
        return __reject()
        pass
            

def __create():
    #try:
        row = db(db.vm_requests.id == request.vars.id).select()[0]
        #return json.dumps(row)
        public_ip_required = row.public_ip_required
        vm = conn.createBaadalVM(row.vm_name, row.image, row.flavor, [{'net-id':row.sec_domain}])
        """create port
            attach floating IP to port
            attach floating IP to VM
        """
        if vm:
            row.update_record(state=2)
            if public_ip_required:
                pass
            return jsonify()
    #except Exception as e:
        return jsonify(status='fail', message=e.message)

def __reject():
    db(db.vm_requests.id == request.vars.id).delete()
    return jsonify()

def __edit():
    pass

def __modify_request():
    try:
        db(db.vm_requests.id == request.vars.id).update(
            extra_storage = request.vars.storage,
            public_ip_required = 1 if request.vars.public_ip == 'yes' else 0,
            flavor = request.vars.flavor)
        db.commit()
        return __create()
    except Exception as e:
        return jsonify(status=fail, message = str(e.__class__))
