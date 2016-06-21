import gluon
import time
from base64 import b64encode
from json import dumps


'''def __do(action, vmid):
    try:
        auth = b64encode(dumps(dict(u=session.username, p=session.password)))
        if action == 'migrate':
            pvars = dict(auth=auth, vmid=vmid)
            scheduler.queue_task(task_migrate_vm, timeout=600, pvars=pvars)
            return jsonify()
        elif action == 'snapshot':
            pvars = dict(auth=auth, vmid=vmid)
            scheduler.queue_task(task_snapshot_vm, timeout=600, pvars=pvars)
            return jsonify()
        elif action == 'restore-snapshot':
            snapshot_id = request.vars.snapshot_id
            pvars = dict(auth=auth, vmid=vmid, snapshot_id=snapshot_id)
            scheduler.queue_task(task_restore_snapshot, timeout=600,
                                 pvars=pvars)
            return jsonify()

        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        vm = conn.find_baadal_vm(id=vmid)
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
        else:
            raise HTTP(400)
        return jsonify(status='success', action=action)
    except Exception as e:
        message = e.message or str(e.__class__)
        logger.exception(message)
        return jsonify(status='fail', message=message)
    finally:
        try:
            conn.close()
        except Exception:
            pass

'''


def __start(vm):
    vm.start()


def __start_resume(vm):
    status = vm.get_status()
    if status == 'Paused':
        vm.resume()
    elif status == 'Shutdown':
        vm.start()


def __shutdown(vm):
    vm.shutdown()


def __pause(vm):
    vm.pause()


def __reboot(vm):
    vm.reboot()


def __delete(vm):
    vm.delete()


def __resume(vm):
    vm.resume()


def __snapshot(vmid):
    auth = b64encode(dumps(dict(u=session.username, p=session.password)))
    pvars = dict(auth=auth, vmid=vmid)
    scheduler.queue_task(task_snapshot_vm, timeout=600, pvars=pvars)


def __clone_vm(vmid):
    import time
    db.clone_requests.insert(vm_id=request.vars.vmid,
                             request_time=int(time.time()),
                             user=session.username,
                             full_clone=1,
                             status=0
                             )
    db.commit()


def __power_off(vm):
    vm.shutdown(force=True)


def __restore_snapshot(vmid):
    auth = b64encode(dumps(dict(u=session.username, p=session.password)))
    snapshot_id = request.vars.snapshot_id
    pvars = dict(auth=auth, vmid=vmid, snapshot_id=snapshot_id)
    scheduler.queue_task(task_restore_snapshot, timeout=600,
                         pvars=pvars)


def __delete_snapshot(vmid):
    auth = b64encode(dumps(dict(u=session.username, p=session.password)))
    snapshot_id = request.vars.snapshot_id
    pvars = dict(auth=auth, vmid=vmid, snapshot_id=snapshot_id)
    logger.debug(pvars)
    scheduler.queue_task(task_delete_snapshot, timeout=600, pvars=pvars)


def __get_console_url(vm):
    console_type = config.get('misc', 'console_type')
    consoleurl = vm.get_console_url(console_type=console_type)
    if request.vars.urlonly:
        return consoleurl
    else:
        return '<a target="_blank" href="{0}">{0}</a>'.format(consoleurl)


def __migrate(vmid):
    pvars = dict(auth=auth, vmid=vmid)
    scheduler.queue_task(task_migrate_vm, timeout=600, pvars=pvars)


@auth.requires_login()
def index():
    action = request.vars.action
    vmid = request.vars.vmid
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        vm = conn.find_baadal_vm(id=vmid)
        if not (user_is_project_admin or session.username in vm.allowed_users):
            raise HTTP(401, body='You are not allowed to perform the ' + \
                    'selected action on the selected VM')
        if action == 'start':
            message = __start(vm)
        elif action == 'shutdown':
            message = __shutdown(vm)
        elif action == 'pause':
            message = __pause(vm)
        elif action == 'restart':
            message = __reboot(vm)
        elif action == 'delete':
            message = __delete(vm)
        elif action == 'resume':
            message = __resume(vm)
        elif action == 'start-resume':
            message = __start_resume(vm)
        elif action == 'snapshot':
            message = __snapshot(vmid)
        elif action == 'get-console-url':
            message = __get_console_url(vm)
        elif action == 'clone':
            message = __clone_vm(vmid)
        elif action == 'poweroff':
            message = __power_off(vm)
        elif action == 'restore-snapshot':
            message = __restore_snapshot(vmid)
        elif action == 'delete-snapshot':
            message = __delete_snapshot(vmid)
        elif action == 'migrate':
            message = __migrate(vmid)
        elif action == 'add-virtual-disk':
            message = __add_virtual_disk(vmid, request.vars.disksize)
        elif action == 'attach-public-ip':
            message =  __attach_public_ip(vmid)
        elif action == 'update-collaborators':
            message =  __update_collaborators(vm)
        message = message or action.capitalize() + ' request has been accepted.'
        return jsonify(message=message)
    except HTTP as e:
        raise e
    except Exception as e:
        logger.exception(e)
        return jsonify(status='fail')

def __update_collaborators(vm):
    if collaborators_is_valid(request.vars.collaborators):
        collaborators = collaborators.strip().split(',')
        collaborators = ','.join([collaborator.strip() for collaborator \
                in collaborators])
        vm.update(collaborators=request.vars.collaborators)
        return 'VM collaborators has been updated successfully'
    else:
        raise HTTP(400, body='Invalid collaborators')


def __add_virtual_disk(vmid, size):
    try:
        db.virtual_disk_requests.insert(user=session.username, vmid=vmid,
                                        disk_size=int(size), status=0)
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))


def __check_public_ip_entry(vmid):
        try:
           row = db((db.floating_ip_requests.status == 0) & (db.floating_ip_requests.vmid == vmid)).select()
           if len(row) > 0:
               return False
           return True
        except Exception as e:
           logger.exception(e)


def __attach_public_ip(vmid):
    try:
       if __check_public_ip_entry(vmid):
            db.floating_ip_requests.insert(vmid=request.vars.vmid,
                                            user=session.username,
                                            status=0
                                           )
            db.commit()
            message = ' Public IP request has been accepted. '
            return message
       else:
            message = ' Public IP request alredy in request queue and waiting for approval'
            return message
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))


@auth.requires(user_is_project_admin)
def handle_disk_request():
    try:
        req = db(db.virtual_disk_requests.id==request.vars.id).select().first()
        if request.vars.action == 'approve':
            size = req.disk_size
            conn = Baadal.Connection(_authurl, _tenant, session.username,
                                     session.password)
            vm = conn.find_baadal_vm(id=req.vmid)
            disk = conn.create_volume(size)
            while disk.status != 'available':
                time.sleep(5)
                disk = conn.get_disk_by_id(disk.id)
            vm.attach_disk(disk)
            req.update_record(status=1)
        elif request.vars.action == 'reject':
            req.delete_record()
        db.commit()
        return jsonify(action=request.vars.action)
    except Exception as e:
        logger.exception(e)
        return jsonify(status='fail', message=e.message or str(e.__class__),
                       action=request.vars.action)


@auth.requires(user_is_project_admin or ldap.user_is_faculty(session.username))
def handle_request():
    action = request.vars.action
    if action == 'approve':
        if user_is_project_admin:
            return __create()
        else:
            raise HTTP(401)
    elif action == 'edit':
        if user_is_project_admin:
            return __modify_request()
        else:
            raise HTTP(401)
    elif action in ('reject', 'delete'):
        return __reject()
    elif action == 'faculty_edit':
        __modify_request()
        return __faculty_approve()
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
    from base64 import b64encode
    from json import dumps
    try:
        row = db(db.vm_requests.id == request.vars.id).select()[0]
        row.update_record(state=REQUEST_STATUS_PROCESSING)
        logger.info('Queuing task')
        auth = b64encode(dumps(dict(u=session.username, p=session.password)))
        scheduler.queue_task(task_create_vm, timeout=600,
                             pvars={'reqid': row.id, 'auth': auth})
        db.commit()
        return jsonify(action='approve')
    except Baadal.BaadalException as e:
        row.update_record(state=REQUEST_STATUS_POSTED)
        logger.exception(e)
        return jsonify(status='fail', message=e.message)
    finally:
        try:
            conn.close()
        except NameError:
            pass


def __reject():
    db(db.vm_requests.id == request.vars.id).delete()
    return jsonify(action='delete')


def __edit():
    pass


def __modify_request():
    try:
        db(db.vm_requests.id == request.vars.id).update(
            extra_storage=request.vars.storage,
            public_ip_required=1 if request.vars.public_ip == 'yes' else 0,
            flavor=request.vars.flavor)
        db.commit()
        return jsonify();
    except Exception as e:
        return jsonify(status='fail', message=str(e.__class__))


def __faculty_approve():
    db(db.vm_requests.id == request.vars.id).update(state=1)
    return jsonify()


@auth.requires(user_is_project_admin)
def handle_account_request():
    try:
        if request.vars.action == 'approve':
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
        else:
            db(db.account_requests.id == request.vars.id).delete()
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
        if request.vars.action == 'reject':
            db(db.resize_requests.id == request.vars.id).delete()
        elif request.vars.action == 'approve':
            row = db(db.resize_requests.id == request.vars.id).select()[0]
            row.update_record(status=REQUEST_STATUS_PROCESSING)
            auth = b64encode(dumps(dict(u=session.username,
                             p=session.password)))
            scheduler.queue_task(task_resize_vm, timeout=600,
                                 pvars={'reqid': row.id, 'auth': auth})
        db.commit()
        return jsonify(action=request.vars.action)
    except Exception as e:
        row.update_record(status=REQUEST_STATUS_POSTED)
        message = e.message or str(e.__class__)
        logger.error(message)
        return jsonify(status='fail', message=message)
    finally:
        try:
            conn.close()
        except:
            pass


def handle_public_ip_request():
    action = request.vars.action
    if action == 'approve':
        return __attach_vm_public_ip()
    elif action == 'reject':
        return __reject_public_ip()

def __reject_public_ip():
    db(db.floating_ip_requests.id == request.vars.id).delete()
    return jsonify(action='reject')

def __attach_vm_public_ip():
    try:
         req = db(db.floating_ip_requests.id==request.vars.id).select().first()
         conn = Baadal.Connection(_authurl, _tenant, session.username,
                                  session.password)
         vm = conn.find_baadal_vm(id=req.vmid)
         vm_name = vm.name
         vm.attach_floating_ip()
         req.update_record(status=1)
         context = Storage()
         context.username = session.username
         context.vm_name = vm_name
         context.mail_support = mail_support
         user_info = ldap.fetch_user_info(session.username)
         context.user_email = user_info['user_email']
         context.gateway_server = gateway_server
         context.req_time = req.request_time
         logger.info('sending mail')
         logger.debug(user_info)
         mailer.send(mailer.MailTypes.IPRequest, context.user_email,
                     context)
         logger.info('mail sent')
         return jsonify(status='success')
    except Exception as e:
         logger.exception(e)
         return jsonify(status='fail', message=e.message or str(e.__class__))
    finally:
         try:
            conn.close()
         except:
            pass

@auth.requires(user_is_project_admin)
def handle_clone_request():
    try:
        if request.vars.action == 'approve':
            row = db(db.clone_requests.id == request.vars.id).select()[0]
            row.update_record(status=REQUEST_STATUS_PROCESSING)
            auth = b64encode(dumps(dict(u=session.username,
                             p=session.password)))
            scheduler.queue_task(task_clone_vm, timeout=600,
                                 pvars={'reqid': row.id, 'auth': auth})
            db.commit()
            return jsonify(message='Request successfully approved')
        elif request.vars.action == 'reject':
            db(db.clone_requests.id == request.vars.id).delete()
            db.commit()
            return jsonify(message='Request successfully deleted')
        else:
            raise HTTP(400)
    except Exception as e:
        message = e.message or str(e.__class__)
        logger.error(message)
        return jsonify(status='fail', message=message)
    finally:
        try:
            conn.close()
        except:
            pass
