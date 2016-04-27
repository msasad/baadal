import gluon
import time


def __do(action, vmid):
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
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
                        return jsonify(snapshotid=snapshotid, action=action)
                    except Exception as e:
                        return jsonify(status='fail', message=e.message,
                                       action=action)
                elif action == 'clone':
                    vm.clone()
                elif action == 'poweroff':
                    vm.shutdown(force=True)
                elif action == 'get-console-url':
                    console_type = config.get('misc', 'console_type')
                    consoleurl = vm.get_console_url(console_type=console_type)
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
        return jsonify(status='fail', message=str(e.message) or str(e.__class__))
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
    import time
    try:
        db.clone_requests.insert(vm_id=request.vars.vmid,
                                 request_time=int(time.time()),
                                 user=session.username,
                                 full_clone=1,
                                 status=0
                                 )
        db.commit()
        return jsonify()
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))
    # return __do('clone', vmid)


def __power_off(vmid):
    return __do('poweroff', vmid)


def __restore_snapshot(vmid):
    return __do('restore-snapshot', vmid)


def __get_console_url(vmid):
    return __do('get-console-url', vmid)


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
    elif action == 'get-console-url':
        return __get_console_url(vmid)
    elif action == 'clone':
        return __clone_vm(vmid)
    elif action == 'poweroff':
        return __power_off(vmid)
    elif action == 'restore-snapshot':
        return __restore_snapshot(vmid)
    elif action == 'migrate':
        return __migrate(vmid)
    elif action == 'add-virtual-disk':
        return __add_virtual_disk(vmid, request.vars.disksize)


def __add_virtual_disk(vmid, size):
    try:
        db.virtual_disk_requests.insert(user=session.username, vmid=vmid,
                                        disk_size=int(size), status=0)
        return jsonify()
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))


@auth.requires(user_is_project_admin)
def handle_disk_request():
    try:
        req = db(db.virtual_disk_requests.id==request.vars.id).select().first()
        size = req.disk_size
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        vm = conn.find_baadal_vm(id=req.vmid)
        disk = conn.create_volume(size)
        while disk.status != 'available':
            time.sleep(1)
            disk = conn.get_disk_by_id(disk.id)
        vm.attach_disk(disk)
        req.update_record(status=1)
        db.commit()
        return jsonify()
    except Exception as e:
        logger.exception(e)
        return jsonify(status='fail', message=e.message or str(e.__class__))


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
    :param public_ip_required: Boolean value to indicate if the newly created
        VM requires floating ip
    :return: None
    """
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
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
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        row = db(db.vm_requests.id == request.vars.id).select()[0]
        public_ip_required = row.public_ip_required
        extra_storage_size = row.extra_storage
        vm = conn.create_baadal_vm(row.vm_name, row.image, row.flavor,
                                   [{'net-id': row.sec_domain}],
                                   key_name=default_keypair)
        """create port
                attach floating IP to port
                attach floating IP to VM
        """
        if vm:
            row.update_record(state=2)
            db.commit()
            if public_ip_required == 1 or extra_storage_size:
                # __finalize_vm(vm, extra_storage_size, public_ip_required)
                thread = FuncThread(__finalize_vm, vm, extra_storage_size,
                                    public_ip_required)
                thread.start()
            context = gluon.tools.Storage()
            context.username = session.username
            context.vm_name = row.vm_name
            context.mail_support = mail_support
            user_info = ldap.fetch_user_info(session.username)
            context.user_email = user_info['user_email']
            context.gateway_server = gateway_server
            context.request_time = seconds_to_localtime(row.request_time)
            mailer.send(mailer.MailTypes.VMCreated, context.user_email,
                        context)
            db.vm_activity_log.insert(vmid=vm.id, user=session.username,
                                      task='create')
            db.commit()
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
        row = db(db.account_requests.id == request.vars.id).select()[0]
        username = row.username
        user_is_faculty = bool(row.faculty_privileges)
        password = row.password
        email = row.email
        userid = row.userid
        ldap.add_user(username, userid, password,
                      user_is_faculty=user_is_faculty, email=email)
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        conn.add_user_role(userid, _tenant, 'user')
        row.update_record(approval_status=1)
        db.commit()
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
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        row = db(db.resize_requests.id == request.vars.id).select()[0]
        vm = conn.find_baadal_vm(id=row.vm_id)
        vm.resize(row['new_flavor'])
        row.update_record(status=1)
        db.commit()
    except Exception as e:
        message = e.message or str(e.__class__)
        logger.error(message)
        return jsonify(status='fail', message=message)
    finally:
        try:
            conn.close()
        except:
            pass


@auth.requires(user_is_project_admin)
def handle_clone_request():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        row = db(db.clone_requests.id == request.vars.id).select()[0]
        vm = conn.find_baadal_vm(id=row.vm_id)
        vm.clone()
        row.update_record(status=1)
        db.commit()
    except Exception as e:
        message = e.message or str(e.__class__)
        logger.error(message)
        return jsonify(status='fail', message=message)
    finally:
        try:
            conn.close()
        except:
            pass
