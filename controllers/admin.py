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


def create_subnet():
    try:
        logger.info(request.vars)

        if request.vars.gateway_ip != '':
            if IS_IPV4()(request.vars.gateway_ip):
                gateway_ip = request.vars.gateway_ip
            else:
                # TODO add each erroneous value to a list and return it to client
                pass
        else:
            gateway_ip = None

        if request.vars.nameservers != '':
            nslist = request.vars.nameservers.translate(None, ' ').split(',')
            for ns in nslist:
                if not IS_IPV4().regex.match(ns):
                    pass
        else:
            nslist = None

        if __validate_ips(request.vars.static_routes):
            routes_list = str_to_route_list(request.vars.static_routes)
        else:
            # TODO send err msg
            pass

        subnet = conn.create_subnet(name=request.vars.subnet_name, network_id=request.vars.net_id,
                                    cidr=request.vars.cidr, ip_version=request.vars.ip_version,
                                    gateway_ip=gateway_ip, enable_dhcp=request.vars.dhcp_enabled,
                                    dns_nameservers=nslist, host_routes=routes_list)
        return jsonify(data=subnet)
    except Exception as e:
        logger.error(e.message or str(e.__class__))
        return jsonify(status='fail')


def __validate_ips(string, replace='\r\n', delim=':'):
    l = string.replace(replace,delim).split(delim)
    for addr in l:
        if not IS_IPV4().regex.match(addr):
            return False
        return True


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
