@auth.requires_login()
def index():
    return dict()


@auth.requires_login()
def request():
    return dict()


def login():
    return dict()


@auth.requires_login()
def my_vms():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        images = dict()
        vms = conn.baadal_vms()
        response = list()
        for vm in vms:
            vm_properties = vm.properties()
            image_id = vm_properties['image']['id']
            if not images.has_key(image_id):
                image = conn.find_image(id=image_id)
                meta = image.metadata
                images[image_id] = ' '.join([meta['os_name'],
                    meta['os_version'], meta['os_arch'],
                    meta['os_edition'], meta['disk_size']])
            vm_properties['image']['info'] = images[image_id]
            response.append(vm_properties)
        #     snapshots = vm.properties()['snapshots']
        #     for index in range(0, len(snapshots)):
        #         snapshots[index]['created'] = convert_timezone(
        #             snapshots[index]['created'])
        #     vm_properties['snapshots'] = snapshots
        return jsonify(data=response)
        #return jsonify(data=vms)
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail')
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires_login()
def vm_status():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        vmid = request.vars.vmid
        vm = conn.find_baadal_vm(id=vmid)
        if vm:
            return jsonify(vm_status=vm.get_status())
    except Exception as e:
        logger.exception(e.message() or str(e.__class__))
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires_login()
def my_requests():
    rows = db(db.vm_requests.requester == session.username and db.vm_requests.state < 2).select()
    l = rows.as_list()
    for i in l:
        # i['flavor'] = flavor_info(i['flavor'])
        i['sec_domain'] = network_name_from_id(i['sec_domain'])
        i['request_time'] = seconds_to_localtime(i['request_time'])
        i['public_ip_required'] = 'Required' if i['public_ip_required'] == 1 \
            else 'Not Required'
        STATES = ['Pending', 'Pending Admin Approval', 'Approved']
        i['state'] = STATES[i['state']]
    return jsonify(data=l)


@auth.requires_login()
def my_requests_list():
    return dict()


def register():
    return dict()
