import json
from novaclient.exceptions import NotFound
import gluon


@auth.requires(user_is_project_admin)
def pending_requests():
    if request.extension in ('', 'html', None):
        return dict()
    elif request.extension == 'json':
        rows = db(db.vm_requests.state < 2).select()
        l = rows.as_list()
        pub_ip = 'public_ip_required'
        flavors = {}
        networks = {}
        for i in l:
            if i['owner'] is None:
                i['owner'] = "IITD Admin"
            if not flavors.has_key(i['flavor']):
                flavors[i['flavor']] = flavor_info(i['flavor'])
            i['flavor'] = flavors[i['flavor']]
            if not networks.has_key(i['sec_domain']):
                networks[i['sec_domain']] = network_name_from_id(i['sec_domain'])
            i['sec_domain'] = networks[i['sec_domain']]
            i['request_time'] = seconds_to_localtime(i['request_time'])
            i[pub_ip] = 'Required' if i[pub_ip] == 1 else 'Not Required'
        return json.dumps({'data': l})


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
        vms = conn.baadal_vms(all_owners=True)
        response = list()
        images = dict()
        for vm in vms:
            vm_properties = vm.properties()
            image_id = vm_properties['image']['id']
            if not images.has_key(image_id):
                try:
                    image = conn.find_image(id=image_id)
                    meta = image.metadata
                    images[image_id] = ' '.join([meta['os_name'],
                        meta['os_version'], meta['os_arch'],
                        meta['os_edition'], meta['disk_size']])
                except NotFound:
                    images[image_id] = 'Image not found'
            vm_properties['image']['info'] = images[image_id]
            #   snapshots = vm.properties()['snapshots']
            #   STR = 'created'
            #   for i in range(0, len(snapshots)):
            #       snapshots[i][STR] = convert_timezone(snapshots[i][STR])
            #   vm_properties['snapshots'] = snapshots
            response.append(vm_properties)
        return jsonify(data=response)
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
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
            del i['password']
            i['request_time'] = seconds_to_localtime(i['request_time'])
            FP = 'faculty_privileges'
            i[FP] = 'Yes' if i[FP] else 'No'
        return jsonify(data=l)


@auth.requires(user_is_project_admin)
def disk_requests():
    if request.extension in ('', None, 'html'):
        return dict()
    elif request.extension == 'json':
        response = []
        spurious_requests = []
        cache = {}
        try:
            rows = db(db.virtual_disk_requests.status == 0).select()
            conn = Baadal.Connection(_authurl, _tenant, session.username,
                                     session.password)
            for row in rows:
                try:
                    cr = {}
                    if not cache.has_key(row.vmid):
                        vm = conn.find_baadal_vm(id=row.vmid)
                        cache[row.vmid] = vm.name
                    cr['vm_name'] = cache[row.vmid]
                    cr['id'] = row.id
                    cr['request_time'] = str(row.request_time)
                    cr['user'] = row.user
                    cr['disk_size'] = row.disk_size
                    response.append(cr)
                except NotFound:
                    spurious_requests.append(str(row.id))
                    continue
            if len(spurious_requests):
                query = 'delete from virtual_disk_requests where id in (%s)' % \
                           (','.join(spurious_requests))
                logger.info('query is ' + query)
                db.executesql(query)
                db.commit()

            return jsonify(data=response)
        except Exception as e:
            logger.exception(e.message or str(e.__class__))
            return jsonify(status='fail', message=e.message or str(e.__class__))
        finally:
            try:
                conn.close()
            except:
                pass


@auth.requires(user_is_project_admin)
def resize_requests():
    if request.extension in ('', None, 'html'):
        return dict()
    elif request.extension == 'json':
        try:
            # TODO Implement caching
            rows = db(db.resize_requests.status == 0).select()
            response = []
            spurious_requests = []
            conn = Baadal.Connection(_authurl, _tenant, session.username,
                                     session.password)
            templates = {}
            for row in rows:
                cr = {}
                try:
                    vm = conn.find_baadal_vm(id=row.vm_id)
                    cr['request_time'] = seconds_to_localtime(row.request_time)
                    cr['user'] = row.user
                    cr['vm_name'] = row.vmname
                    cr['id'] = row.id
                except NotFound:
                    spurious_requests.append(str(row.id))
                    continue
                flavor_id = vm.server.flavor['id']
                if not templates.has_key(flavor_id):
                    temp = conn.find_template(id=flavor_id)
                    templates[flavor_id] = 'RAM : %s, vCPUs: %s' % (temp.ram,
                                                                   temp.vcpus)
                cr['current_config'] = templates[flavor_id]

                flavor_id = row.new_flavor
                if not templates.has_key(flavor_id):
                    temp = conn.find_template(id=flavor_id)
                    templates[flavor_id] = 'RAM : %s, vCPUs: %s' % (temp.ram,
                                                                   temp.vcpus)
                cr['requested_config'] = templates[flavor_id]
                response.append(cr)
            if len(spurious_requests):
                query = 'delete from resize_requests where id in (%s)' % \
                           (','.join(spurious_requests))
                db.executesql(query)
                db.commit()
            return jsonify(data=response)
        except Exception as e:
            logger.exception(e.message or str(e.__class__))
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
            response = []
            conn = Baadal.Connection(_authurl, _tenant, session.username,
                                     session.password)
            spurious_requests = []
            for row in rows:
                cr = dict()
                cr['request_time'] = seconds_to_localtime(row.request_time)
                cr['id'] = row.id
                cr['vm_id'] = row.vm_id
                cr['full_clone'] = 'Yes' if row['full_clone'] == 1 else 'No'
                cr['clone_name'] = row.clone_name
                cr['user'] = row.user
                try:
                    vm = conn.find_baadal_vm(id=row.vm_id)
                    cr['vm_name'] = vm.name
                    response.append(cr)
                except NotFound:
                    spurious_requests.append(str(row.id))
                    continue
            if len(spurious_requests):
                query = 'delete from clone_requests where id in (%s)' % \
                           (','.join(spurious_requests))
                db.executesql(query)
                db.commit()
            return jsonify(data=response)
        except Exception as e:
            logger.exception(e)
            raise HTTP(500, body=jsonify(status='fail',
                           message=e.message or str(e.__class__)))
        finally:
            try:
                conn.close()
            except:
                pass



@auth.requires(user_is_project_admin)
def public_ip_requests():
    if request.extension in ('', None, 'html'):
        return dict()
    elif request.extension == 'json':
        try:
            rows = db(db.floating_ip_requests.status == 0).select()
            response = []
            conn = Baadal.Connection(_authurl, _tenant, session.username,
                                     session.password)
            spurious_requests = []
            for row in rows:
                cr = {}
                try:
                    vm = conn.find_baadal_vm(id=row.vmid)
                    cr['request_time'] = str(row.request_time)
                    cr['user'] = row.user
                    cr['vmid'] = vm.name
                    cr['id'] = row.id
                    response.append(cr)
                except NotFound:
                    spurious_requests.append(str(row.id))
                    continue
            if len(spurious_requests):
                query = 'delete from public_ip_requests where id in (%s)' % \
                           (','.join(spurious_requests))
                db.executesql(query)
                db.commit()
            return jsonify(data=response)
        except Exception as e:
            logger.exception(e)
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

@auth.requires(user_is_project_admin)
def test():
    scheduler.queue_task(test)
    return jsonify()
