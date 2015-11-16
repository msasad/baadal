import json


def pending_requests():
    rows = db(db.vm_requests.state == 0).select()
    l = rows.as_list()
    for i in l:
        i['flavor'] = flavor_info(i['flavor'])
        i['sec_domain'] = network_name_from_id(i['sec_domain'])
        i['request_time'] = seconds_to_localtime(i['request_time'])
        i['public_ip_required'] = 'Required' if i['public_ip_required'] == 1 else 'Not Required'
    return json.dumps({'data': l})
    pass


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


def secgroups():
    try:
        secgroupslist = conn.sgroups()
        return jsonify(data=secgroupslist)
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail')


def hostinfo():
    try:
        hostid = request.vars.id
        hypervisors = conn.hypervisors(id=hostid)
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


def all_vms():
    try:
        vms = conn.baadal_vms(True)
        response = list()
        for vm in vms:
            vm_properties = vm.properties()
            snapshots = vm.properties()['snapshots']
            for i in range(0, len(snapshots)):
                snapshots[i]['created'] = convert_timezone(snapshots[i]['created'])
            vm_properties['snapshots'] = snapshots
            response.append(vm_properties)
        return jsonify(data=response)
    except Exception as e:
        logger.error(e.message or str(e.__class__))
        return jsonify(status='fail')


# Empty controllers for HTML files
def pending_requests_list():
    return dict()


def floatingips():
    return dict()


def hosts():
    return dict()


def configure():
    return dict()


def networking():
    return dict()


def security_groups():
    return dict()


def index():
    return dict()
    pass
