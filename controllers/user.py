def index():
    return dict()


def request():
    return dict()


def login():
    return dict()


def my_vms():
    import json
    vms = conn.baadalVMs()
    response = list()
    for vm in vms:
        response.append(vm.properties())

    return json.dumps({'data': response})


def vm_status():
    vmid = request.vars.vmid
    vm = conn.findBaadalVM(id=vmid)
    if vm:
        return jsonify(vm_status=vm.getStatus())


def my_requests():
    # import json
    rows = db(db.vm_requests.owner == 'test').select()
    l = rows.as_list()
    return jsonify(data=l)


def my_requests_list():
    return dict()
