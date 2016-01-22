import json

@auth.requires(user_is_project_admin)
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


@auth.requires(user_is_project_admin)
def networks():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        networklist = conn.networks()['networks']
        for network in networklist:
            network['subnets'] = conn.subnets(network['id'])['subnets']
        return jsonify(data=networklist)
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail', message=e.message)
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires(user_is_project_admin)
def subnets():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        subnet_list = conn.subnets(request.vars.netid)
        return jsonify(data=subnet_list)
    except Exception as e:
        logger.debug(e.message)
        return jsonify('fail', message=e.message)
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires(user_is_project_admin)
def secgroups():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        secgroupslist = conn.sgroups()
        return jsonify(data=secgroupslist)
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail')
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires(user_is_project_admin)
def hostinfo():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        hostid = request.vars.id
        hypervisors = conn.hypervisors(id=hostid)
        return jsonify(data=[h.to_dict() for h in hypervisors])
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail')
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires(user_is_project_admin)
def hostaction():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        hostname = request.vars.hostname
        action = request.vars.action
        conn.nova.hosts.host_action(hostname, action)
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail')
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires(user_is_project_admin)
def all_vms():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
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
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires(user_is_project_admin)
def create_subnet():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        logger.info(request.vars)

        gateway_ip = None
        if request.vars.gateway_ip != '':
            if IS_IPV4()(request.vars.gateway_ip):
                gateway_ip = request.vars.gateway_ip
            else:
                # TODO add each erroneous value to a list and return it to client
                pass

        if request.vars.nameservers != '':
            nslist = request.vars.nameservers.translate(None, ' ').split(',')
            for ns in nslist:
                if not IS_IPV4().regex.match(ns):
                    pass
        else:
            nslist = None

        routes_list = str_to_route_list(request.vars.static_routes) if request.vars.static_routes != '' else None

        if request.vars.allocation_pool != '':
            allocation_pool_start, allocation_pool_end = request.vars.allocation_pool.translate(None, ' ').split('-')
        else:
            allocation_pool_end = allocation_pool_start = None

        subnet = conn.create_subnet(name=request.vars.subnet_name, network_id=request.vars.net_id,
                                    cidr=request.vars.cidr, ip_version=request.vars.ip_version,
                                    gateway_ip=gateway_ip, enable_dhcp=request.vars.dhcp_enabled,
                                    dns_nameservers=nslist, host_routes=routes_list,
                                    allocation_pool_start=allocation_pool_start,
                                    allocation_pool_end=allocation_pool_end)
        return jsonify(data=subnet)
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))
    finally:
        try:
            conn.close()
        except NameError:
            pass


def __validate_ips(string, replace='\r\n', delim=':'):
    l = string.replace(replace, delim).split(delim)
    for addr in l:
        if not IS_IPV4().regex.match(addr):
            return False
        return True


@auth.requires(user_is_project_admin)
def create_network():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        network = conn.create_network(request.vars.net_name, request.vars.segmentation_id,
                                      shared=request.vars.shared, external=request.vars.external,
                                      admin_state_up=request.vars.network_up)

        try:
            sg_id = conn.create_security_group(request.vars.net_name)['security_group']['id']
            conn.create_security_group_rule(sg_id=sg_id, direction='egress', remote_group=sg_id)
            conn.create_security_group_rule(sg_id=sg_id, direction='ingress', remote_group=sg_id)
        except Exception as e:
            logger.error('Failed to create Security group for new network')
            logger.exception(e.message or str(e.__class__))
            conn.delete_network(network['network']['id'])
            logger.info('Deleted the newly created network')
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))
    finally:
        try:
            conn.close()
        except NameError:
            pass


# Empty controllers for HTML files
@auth.requires(user_is_project_admin)
def pending_requests_list():
    return dict()


@auth.requires(user_is_project_admin)
def floatingips():
    return dict()


@auth.requires(user_is_project_admin)
def hosts():
    return dict()


@auth.requires(user_is_project_admin)
def configure():
    return dict()


@auth.requires(user_is_project_admin)
def networking():
    return dict()


@auth.requires(user_is_project_admin)
def security_groups():
    return dict()


@auth.requires(user_is_project_admin)
def index():
    return dict()
    pass
