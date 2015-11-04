import json
from log_handler import logger
# import log_handler.mylogger as mylogger


def index():
    return dict()
    pass


def pending_requests():
    rows = db(db.vm_requests.state == 0).select()
    # rows = db().select(db.vm_requests.ALL)
    l = rows.as_list()
    for i in l:
        i['sec_domain'] = network_name_from_id(i['sec_domain'])
        i['request_time'] = seconds_to_localtime(i['request_time'])
        i['public_ip_required'] = 'Required' if i['public_ip_required'] == 1 else 'Not Required'
        # i['sec_domain']  = conn.findNetwork(id=i['sec_domain']).name
    return json.dumps({'data': l})
    pass


def pending_requests_list():
    return dict()


def handle_request():
    status = {'edit': 'edited', 'approve': 'approved', 'reject': 'rejected'}
    # rid = request.vars.id
    action = request.vars.action
    if action == 'approve':
        try:
            row = db(db.vm_requests.id == request.vars.id).select()[0]
            vm = conn.createBaadalVM(row.name, row.image, row.flavor)
            if vm:
                return jsonify()
        except Exception as e:
            return json.dumps({'status': 'fail', 'message': e.message})
        # vm = conn.createBaadalVM()
    return json.dumps({'message': 'Request id %s is %s' % (request.vars.id, status[request.vars.action])})


def configure():
    return dict()


def networking():
    return dict()


def networks():
    try:
        networklist = conn.networks()['networks']
        for network in networklist:
            network['subnets'] = conn.subnets(network['id'])['subnets']
        return jsonify(data=networklist)
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail', message=e.message)


def subnets():
    try:
        subnet_list = conn.subnets(request.vars.netid)
        return jsonify(data=subnet_list)
    except Exception as e:
        logger.debug(e.message)
        return jsonify('fail', message=e.message)


def hosts():
    return dict()


def secgroups():
    try:
        secgroups = conn.sgroups()
        return json.dumps(secgroups.to_dict())
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail')


def floatingips():
    return dict()


def hostinfo():
    try:
        id = request.vars.id
        hypervisors = conn.hypervisors(id=id)
        return jsonify(data=[h.to_dict() for h in hypervisors])
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail')


def hostaction():
    try:
        hostname = request.vars.hostname
        action = request.vars.action
        conn.nova.hosts.host_action(hostname, action)
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail')

