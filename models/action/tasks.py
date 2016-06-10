from base64 import b64decode
from json import loads
from gluon.tools import Storage
from time import sleep


def task_create_vm(reqid, auth):
    logger.debug('inside scheduler')
    try:
        auth = Storage(loads(b64decode(auth)))
        req = db(db.vm_requests.id == reqid).select()[0]
        conn = Baadal.Connection(_authurl, _tenant, auth.u, auth.p)
        name = req.vm_name
        img = req.image
        flavor = req.flavor
        nics = [{'net-id': req.sec_domain}]
        kp = default_keypair
        pub_ip = req.public_ip_required
        vdisk = req.extra_storage
        vm = conn.create_baadal_vm(name, img, flavor, nics, key_name=kp)
        status = vm.get_status()
        while status not in ('Running', 'Error'):
            logger.info('VM %s in creation, current status %s' % \
                        (name, status))
            sleep(5)
            status = vm.get_status()
        if status == 'Running':
            logger.info('VM created')
            try:
                req.update_record(state=REQUEST_STATUS_APPROVED)
                context = Storage()
                user_info = ldap.fetch_user_info(auth.u)
                context.username = user_info['user_name']
                context.user_email = user_info['user_email']
                context.vm_name = name
                context.mail_support = mail_support
                context.gateway_server = gateway_server
                context.request_time = seconds_to_localtime(req.request_time)
                logger.info('sending mail')
                mailer.send(mailer.MailTypes.VMCreated, context.user_email,
                            context)
                logger.info('mail sent')
                if pub_ip == 1 or vdisk:
                    if pub_ip:
                        vm.attach_floating_ip()

                    if vdisk:
                        disk = conn.create_volume(vdisk)
                        while disk.status != 'available':
                            disk = conn.get_disk_by_id(disk.id)
                        num_disks = vm.metadata()['disks']
                        disk_path = '/dev/vd' + chr(97 + num_disks)
                        vm.attach_disk(disk, disk_path)
                        vm.update(disks=num_disks + 1)
            except Exception as e:
                logger.exception(e)
        else:
            # VM state Error
            req.update_record(state=REQUEST_STATUS_POSTED)
            raise Exception('VM build failed')
    except Exception as e:
        req.update_record(state=REQUEST_STATUS_POSTED)
        logger.exception(e)
    finally:
        db.commit()


def task_migrate_vm(auth, vmid, live=False, destination=None):
    auth = Storage(loads(b64decode(auth)))
    conn = Baadal.Connection(_authurl, _tenant, auth.u, auth.p)
    if live:
        pass
    else:
        pass


def task_snapshot_vm(auth, vmid):
    auth = Storage(loads(b64decode(auth)))
    try:
        conn = Baadal.Connection(_authurl, _tenant, auth.u, auth.p)
        vm = conn.find_baadal_vm(id=vmid)
        snapshot_id = vm.create_snapshot()
        logger.info('Snapshot created: VMID %s, snapshot_id %s' % \
                (vmid, snapshot_id))
    except Exception as e:
        logger.exception(e)


def task_restore_snapshot(auth, vmid, snapshot_id):
    auth = Storage(loads(b64decode(auth)))
    try:
        conn = Baadal.Connection(_authurl, _tenant, auth.u, auth.p)
        vm = conn.find_baadal_vm(id=vmid)
        vm.restore_snapshot(snapshot_id)
        logger.info('Snapshot restored: VMID %s, snapshot_id %s' % \
                (vmid, snapshot_id))
    except Exception as e:
        logger.exception(e)


def task_delete_snapshot(auth, vmid, snapshot_id):
    auth = Storage(loads(b64decode(auth)))
    try:
        conn = Baadal.Connection(_authurl, _tenant, auth.u, auth.p)
        image = conn.find_image(id=snapshot_id)
        status = image.delete()
        logger.info('Snapshot deleted: VMID %s, snapshot_id %s' % \
                (vmid, snapshot_id))
    except Exception as e:
        logger.exception(e)

def task_clone_vm(auth, reqid):
    auth = Storage(loads(b64decode(auth)))
    req = db(db.clone_requests.id == reqid).select()[0]
    try:
        conn = Baadal.Connection(_authurl, _tenant, auth.u, auth.p)
        vm = conn.find_baadal_vm(id=req.vm_id)
        clone = vm.clone()
        logger.info('VM Cloned: VMID %s, clone_id %s' % (req.vm_id, clone))
        req.update_record(status=REQUEST_STATUS_APPROVED)
    except Exception as e:
        logger.exception(e)
        req.update_record(status=REQUEST_STATUS_POSTED)

def task_resize_vm(auth, reqid):
    auth = Storage(loads(b64decode(auth)))
    logger.info('Resizing VM')
    try:
        req = db(db.resize_requests.id == reqid).select()[0]
        conn = Baadal.Connection(_authurl, _tenant, auth.u, auth.p)
        vm = conn.find_baadal_vm(id=req.vm_id)
        new_flavor = req.new_flavor
        vm.resize(new_flavor)
        req.update_record(status=REQUEST_STATUS_APPROVED)
        logger.info('VM Resized: VMID %s, old_flavor %s, new_flavor %s' % \
                    (req.vm_id, vm.server.flavor['id'], req.new_flavor))
    except Exception as e:
        logger.exception(e)
        req.update_record(status=REQUEST_STATUS_POSTED)
    finally:
        db.commit()
        conn.close()



