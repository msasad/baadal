import json
import gluon


@auth.requires(user_is_project_admin)
def pending_requests():
    rows = db(db.vm_requests.state < 2).select()
    l = rows.as_list()
    pub_ip = 'public_ip_required'
    for i in l:
        i['flavor'] = flavor_info(i['flavor'])
        i['sec_domain'] = network_name_from_id(i['sec_domain'])
        i['request_time'] = seconds_to_localtime(i['request_time'])
        i[pub_ip] = 'Required' if i[pub_ip] == 1 else 'Not Required'
    return json.dumps({'data': l})
    pass


@auth.requires(user_is_project_admin)
def networks():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
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
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
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
def security_groups():
    if request.extension in ('', 'html', None):
        return dict()
    elif request.extension == 'json':
        try:
            conn = Baadal.Connection(_authurl, _tenant, session.username,
                                     session.password)
            tenant_id = conn.get_tenant_id()
            sgroupslist = conn.sgroups(tenant_id=tenant_id)['security_groups']
            return jsonify(data=sgroupslist)
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
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
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
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
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
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        vms = conn.baadal_vms(True)
        response = list()
        for vm in vms:
            vm_properties = vm.properties()
            snapshots = vm.properties()['snapshots']
            STR = 'created'
            for i in range(0, len(snapshots)):
                snapshots[i][STR] = convert_timezone(snapshots[i][STR])
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
    fields = validate_subnet_form(request.vars)
    if len(fields):
        raise HTTP(400,body=jsonify(status='fail', fields=fields))

    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        if request.vars.gateway_ip == '':
            gateway_ip = None

        if request.vars.nameservers == '':
            nslist = None

        routes_list = str_to_route_list(request.vars.static_routes)\
            if request.vars.static_routes != '' else None

        if request.vars.allocation_pool != '':
            allocation_pool = request.vars.allocation_pool.\
                translate(None, ' ').split('-')
        else:
            allocation_pool = [None, None]

        subnet = conn.create_subnet(name=request.vars.subnet_name,
                                    network_id=request.vars.net_id,
                                    cidr=request.vars.cidr,
                                    ip_version=request.vars.ip_version,
                                    gateway_ip=gateway_ip,
                                    enable_dhcp=request.vars.dhcp_enabled,
                                    dns_nameservers=nslist,
                                    host_routes=routes_list,
                                    allocation_pool_start=allocation_pool[0],
                                    allocation_pool_end=allocation_pool[1])
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
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        network = conn.create_network(request.vars.net_name,
                                      request.vars.segmentation_id,
                                      shared=request.vars.shared,
                                      external=request.vars.external,
                                      admin_state_up=request.vars.network_up)

        try:
            sg = conn.create_security_group(request.vars.net_name)
            sg_id = sg['security_group']['id']
            conn.create_security_group_rule(sg_id=sg_id, direction='egress',
                                            remote_group=sg_id)
            conn.create_security_group_rule(sg_id=sg_id, direction='ingress',
                                            remote_group=sg_id)
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
def account_requests():
    if request.extension in ('', None, 'html'):
        return dict()
    elif request.extension == 'json':
        rows = db(db.account_requests.approval_status == 0).select()
        l = rows.as_list()
        for i in l:
            i['request_time'] = seconds_to_localtime(i['request_time'])
            FP = 'faculty_privileges'
            i[FP] = 'Yes' if i[FP] else 'No'
        return jsonify(data=l)


@auth.requires(user_is_project_admin)
def resize_requests():
    if request.extension in ('', None, 'html'):
        return dict()
    elif request.extension == 'json':
        try:
            # TODO: Return a list of dictionaries with following keys
            # user,
            # vm_name,
            # vm_id
            # current_config,
            # requested_config,
            # request_time
            rows = db(db.resize_requests.status == 0).select()
            l = rows.as_list()
            conn = Baadal.Connection(_authurl, _tenant, session.username,
                                     session.password)
            for i in l:
                i['request_time'] = seconds_to_localtime(i['request_time'])
                vm = conn.find_baadal_vm(id=i['vm_id'])
                i['vm_name'] = vm.name
                templ = conn.find_template(id=vm.server.flavor['id'])
                i['current_config'] = 'RAM : %s, vCPUs: %s' % (templ.ram,
                                                               templ.vcpus)
                templ = conn.find_template(id=i['new_flavor'])
                i['requested_config'] = 'RAM : %s, vCPUs: %s' % (templ.ram,
                                                                 templ.vcpus)
            return jsonify(data=l)
        except Exception as e:
            logger.error(e.message or str(e.__class__))
            return jsonify(status='fail',
                           message=e.message or str(e.__class__))
        finally:
            try:
                conn.close()
            except:
                pass


@auth.requires(user_is_project_admin)
def clone_requests():
    if request.extension in ('', None, 'html'):
        return dict()
    elif request.extension == 'json':
        try:
            rows = db(db.clone_requests.status == 0).select()
            l = rows.as_list()
            conn = Baadal.Connection(_authurl, _tenant, session.username,
                                     session.password)
            for i in l:
                i['request_time'] = seconds_to_localtime(i['request_time'])
                vm = conn.find_baadal_vm(id=i['vm_id'])
                i['vm_name'] = vm.name
                i['full_clone'] = 'Yes' if i['full_clone'] == 1 else 'No'
            return jsonify(data=l)
        except Exception as e:
            logger.error(e.message or str(e.__class__))
            return jsonify(status='fail',
                           message=e.message or str(e.__class__))
        finally:
            try:
                conn.close()
            except:
                pass


@auth.requires(user_is_project_admin)
def index():
    return dict()
    pass
