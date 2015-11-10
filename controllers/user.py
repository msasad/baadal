def index():
    return dict()


def request():
    return dict()


def login():
    return dict()


def my_vms():
    vms = conn.baadal_vms()
    response = list()
    for vm in vms:
        vm_properties = vm.properties()
        snapshots = vm.properties()['snapshots']
        for index in range(0, len(snapshots)):
            snapshots[index]['created'] = convert_timezone(snapshots[index]['created'])
        vm_properties['snapshots'] = snapshots
        response.append(vm_properties)
    return jsonify(data=response)


def vm_status():
    vmid = request.vars.vmid
    vm = conn.find_baadal_vm(id=vmid)
    if vm:
        return jsonify(vm_status=vm.get_status())


def my_requests():
    # FIXME: Remove hardcoded username
    rows = db(db.vm_requests.owner == 'test').select()
    l = rows.as_list()
    return jsonify(data=l)


def my_requests_list():
    return dict()
