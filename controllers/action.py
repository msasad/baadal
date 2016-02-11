def __do(action, vmid):
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        if conn:
            vm = conn.find_baadal_vm(id=vmid)
            if vm:
                if action == 'start':
                    vm.start()
                elif action == 'migrate':
                    vm.migrate()
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
                        snapshotid = vm.create_snapshot()
                        return jsonify(snapshotid=snapshotid)
                    except Exception as e:
                        return jsonify(status='fail', message=e.message, action=action)
                elif action == 'clone':
                    vm.clone()
                elif action == 'poweroff':
                    vm.shutdown(force=True)
                elif action == 'get-vnc-console':
                    consoleurl = vm.get_console_url()
                    return jsonify(consoleurl=consoleurl, action=action)
                elif action == 'get-spice-console':
                    consoleurl = vm.get_console_url(console_type='spice')
                    return jsonify(consoleurl=consoleurl, action=action)
                elif action == 'start-resume':
                    status = vm.get_status()
                    if status == 'Paused':
                        vm.resume()
                    elif status == 'Shutdown':
                        vm.start()
            conn.close()
            return jsonify(status='success', action=action)
        else:
            conn.close()
            return jsonify(status='failure')
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
    finally:
        try:
            conn.close()
        except Exception:
            pass


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
    return __do('poweroff', vmid)


def __restore_snapshot(vmid):
    return __do('restore-snapshot', vmid)


def __get_vnc_console(vmid):
    return __do('get-vnc-console', vmid)

def __get_spice_console(vmid):
    return __do('get-spice-console', vmid)

def __migrate(vmid):
    return __do('migrate', vmid)


@auth.requires_login()
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
    elif action == 'get-spice-console':
        return __get_spice_console(vmid)
    elif action == 'clone':
        return __clone_vm(vmid)
    elif action == 'poweroff':
        return __power_off(vmid)
    elif action == 'restore-snapshot':
        return __restore_snapshot(vmid)
    elif action == 'migrate':
        return  __migrate(vmid)


@auth.requires(user_is_project_admin)
def handle_request():
    action = request.vars.action
    if action == 'approve':
        return __create()
    elif action == 'edit':
        __modify_request()
        return __create()
        pass
    elif action == 'reject':
        return __reject()
        pass
    elif action == 'faculty_edit':
        __modify_request()
        return __faculty_approve()
        pass
    elif action == 'faculty_approve':
        return __faculty_approve()


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
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        while vm.get_status() != 'Running' and vm.get_status() != 'Error':
            pass

        if vm.get_status() == 'Running':
            if public_ip_required:
                vm.attach_floating_ip()

            if extra_storage_size:
                disk = conn.create_volume(extra_storage_size)
                while disk.status != 'available':
                    disk = conn.get_disk_by_id(disk.id)
                num_disks = vm.metadata()['disks']
                disk_path = '/dev/vd' + chr(97 + num_disks)
                vm.attach_disk(disk, disk_path)
                vm.update(disks=num_disks + 1)
        else:
            raise Baadal.BaadalException('VM Build Failed')
    except Exception as e:
        logger.error(e.message)
    finally:
        try:
            conn.close()
        except NameError:
            pass


def __create():
    try:  
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        row = db(db.vm_requests.id == request.vars.id).select()[0]
        public_ip_required = row.public_ip_required
        extra_storage_size = row.extra_storage
        vm = conn.create_baadal_vm(row.vm_name, row.image, row.flavor, [{'net-id': row.sec_domain}])
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
    except Baadal.BaadalException as e:
        logger.exception(e.message)
        return jsonify(status='fail')
    finally:
        try:
            conn.close()
        except NameError:
            pass


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
    except Exception as e:
        return jsonify(status='fail', message=str(e.__class__))

def __faculty_approve():
    db(db.vm_requests.id == request.vars.id).update(state=1)
    return jsonify()


@auth.requires(user_is_project_admin)
def handle_account_request():
    try:
        l = BaadalLDAP.BaadalLDAP(ldap_host, ldap_base_dn, ldap_admin_dn, ldap_admin_password)
        row = db(db.account_requests.id == request.vars.id).select()[0]
        username = row.username
        user_is_faculty = bool(row.faculty_privileges)
        password = row.password
        email = row.email
        userid = row.userid
        l.add_user(username, userid, password, user_is_faculty=user_is_faculty, email=email)
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        conn.add_user_role(userid, _tenant, 'user')
        row.update_record(approval_status = 1)
        return jsonify()
    except Exception as e:
        logger.error(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))
    finally:
        try:
            conn.close()
        except:
            pass


@auth.requires(user_is_project_admin)
def handle_resize_request():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username, session.password)
        row = db(db.account_requests.id == request.vars.id).select()[0]
        vm = conn.find_baadal_vm(id=row.vm_id)
        vm.resize(row['new_flavor'])
    except Exception as e:
        message = e.message or str(e.__class__)
        logger.error(message)
        return jsonify(status='fail', message=message)
    finally:
        try:
            conn.close()
        except:
            pass
