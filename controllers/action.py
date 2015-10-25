def __do(action, vmid):
    # conn = Baadal.Connection("http://10.237.23.178:35357/v2.0", "admin", "admin", "baadal")
    if conn:
        vm = conn.findBaadalVM(id=vmid)
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
        return jsonify()
    else:
        conn.close()
        return jsonify(status='failure')


def __start():
    return __do('start', request.vars.vmid)


def __shutdown():
    return __do('shutdown', request.vars.vmid)


def __pause():
    return __do('pause', request.vars.vmid)


def __reboot():
    return __do('reboot', request.vars.vmid)


def __delete():
    return __do('delete', request.vars.vmid)


def __resume():
    return __do('resume', request.vars.vmid)


def vm_action():
    action = request.vars.action
    if action == 'start':
        return __start()
    elif action == 'shutdown':
        return __shutdown()
    elif action == 'pause':
        return __pause()
    elif action == 'restart':
        return __reboot()
    elif action == 'delete':
        return __delete()
    elif action == 'resume':
        return __resume()


def handle_request():
    action = request.vars.action
    if action == 'approve':
        return __create()
    elif action == 'edit':
        return __modify_request()
        pass
    elif action == 'reject':
        return __reject()
        pass


def __finalize_vm(vm, extra_storage_size, public_ip_required=False):
    while vm.getStatus() != 'Running' and vm.getStatus() != 'Error':
        pass

    if vm.getStatus() == 'Running':
        if public_ip_required:
            vm.attachFloatingIP()

        if extra_storage_size:
            disk = conn.createVolume(extra_storage_size)
            while disk.status != 'available':
                disk = conn.getDiskById(disk.id)
            vm.attachDisk(disk, '/dev/vdb')
            vm.update(disks=2)
    else:
        raise Exception('VM Build Failed')


def __create():
    # try:
    row = db(db.vm_requests.id == request.vars.id).select()[0]
    # return json.dumps(row)
    public_ip_required = row.public_ip_required
    extra_storage_size = row.extra_storage
    vm = conn.createBaadalVM(row.vm_name, row.image, row.flavor, [{'net-id': row.sec_domain}])
    """create port
            attach floating IP to port
            attach floating IP to VM
    """
    if vm:
        row.update_record(state=2)
        db.commit()
        if public_ip_required == 1 or extra_storage_size:
            __finalize_vm(vm, extra_storage_size, public_ip_required)
            # thread = FuncThread(__finalize_vm, vm, extra_storage_size, public_ip_required)
            # thread.start()
            pass
        return jsonify()
        # except Exception as e:
    return jsonify(status='fail')  # message=e.message)


def __reject():
    db(db.vm_requests.id == request.vars.id).delete()
    return jsonify()


def __edit():
    pass


def __modify_request():
    try:
        db(db.vm_requests.id == request.vars.id).update(
            extra_storage=request.vars.storage,
            public_ip_required=1 if request.vars.public_ip == 'yes' else 0,
            flavor=request.vars.flavor)
        db.commit()
        return __create()
    except Exception as e:
        return jsonify(status='fail', message=str(e.__class__))
