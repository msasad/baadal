from log_handler import logger


def __do(action, vmid):
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
            elif action == 'restore-snapshot':
                vm.restore_snapshot(request.vars.snapshot_id)
            elif action == 'snapshot':
                try:
                    snapshotid = vm.createSnapshot()
                    return jsonify(snapshotid=snapshotid)
                except Exception as e:
                    return jsonify(status='fail', message=e.message, action=action)
            elif action == 'clone':
                vm.clone()
            elif action == 'powerOff':
                vm.shutdown(force=True)
            elif action == 'get-vnc-console':
                consoleurl = vm.getVNCConsole()
                return jsonify(consoleurl=consoleurl, action=action)
            elif action == 'start-resume':
                status = vm.getStatus()
                if status == 'Paused':
                    vm.resume()
                elif status == 'Shutdown':
                    vm.start()
        conn.close()
        return jsonify(status='success', action=action)
    else:
        conn.close()
        return jsonify(status='failure')


def __start(vmid):
    return __do('start', vmid)


def __start_resume(vmid):
    return __do('start-resume', vmid)


def __shutdown(vmid):
    return __do('shutdown', vmid)


def __pause(vmid):
    return __do('pause', vmid)


def __reboot(vmid):
    return __do('reboot', vmid)


def __delete(vmid):
    return __do('delete', vmid)


def __resume(vmid):
    return __do('resume', vmid)


def __snapshot(vmid):
    return __do('snapshot', vmid)


def __clone_vm(vmid):
    return __do('clone', vmid)


def __power_off(vmid):
    return __do('powerOff', vmid)


def __restore_snapshot(vmid):
    return __do('restore-snapshot', vmid)


def __get_vnc_console(vmid):
    return __do('get-vnc-console', vmid)


def index():
    action = request.vars.action
    vmid = request.vars.vmid
    if action == 'start':
        return __start(vmid)
    elif action == 'shutdown':
        return __shutdown(vmid)
    elif action == 'pause':
        return __pause(vmid)
    elif action == 'restart':
        return __reboot(vmid)
    elif action == 'delete':
        return __delete(vmid)
    elif action == 'resume':
        return __resume(vmid)
    elif action == 'start-resume':
        return __start_resume(vmid)
    elif action == 'snapshot':
        return __snapshot(vmid)
    elif action == 'get-vnc-console':
        return __get_vnc_console(vmid)
    elif action == 'clone':
        return __clone_vm(vmid)
    elif action == 'powerOff':
        return __power_off(vmid)
    elif action == 'restore-snapshot':
        return __restore_snapshot(vmid)


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
    """
    Attaches extra storage and/or assigns public IP to a newly created VM.
    This function is specially meant to be run on a separate thread
    :param vm: BaadalVM object representing the newly created VM
    :param extra_storage_size: Integer size of extra disk to be attached
    :param public_ip_required: Boolean value to indicate if the newly created VM requires floating ip
    :return: None
    """

    try:
        while vm.getStatus() != 'Running' and vm.getStatus() != 'Error':
            pass

        if vm.getStatus() == 'Running':
            if public_ip_required:
                vm.attachFloatingIP()

            if extra_storage_size:
                disk = conn.createVolume(extra_storage_size)
                while disk.status != 'available':
                    disk = conn.getDiskById(disk.id)
                num_disks = vm.metadata()['disks']
                disk_path = '/dev/vd' + chr(97 + num_disks)
                vm.attachDisk(disk, disk_path)
                vm.update(disks=num_disks + 1)
        else:
            raise Baadal.BaadalException('VM Build Failed')
    except Exception as e:
        logger.error(e.message)


def __create():
    try:
        row = db(db.vm_requests.id == request.vars.id).select()[0]
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
                # __finalize_vm(vm, extra_storage_size, public_ip_required)
                thread = FuncThread(__finalize_vm, vm, extra_storage_size, public_ip_required)
                thread.start()
                pass
            return jsonify()
    except Exception as e:
        return jsonify(status='fail')


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
