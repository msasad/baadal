import Baadal
import json
import ConfigParser

# work around to stop stupid editors from complaining about undeclared 'request'
if False:
    request = dict()
config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')
authurl = config.get('auth','authurl')
tenant = config.get('auth','tenant')
password = config.get('auth','password')
username = config.get('auth', 'username')

def __do(action, vmid):
    
    conn = Baadal.Connection(authurl, tenant, username, password)
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
        return json.dumps(dict(status='success', code='OK'))
    else:
        conn.close()
        return dict(res = json.dumps(dict(status='failure')))

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
