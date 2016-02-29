import time


@auth.requires_login()
def new_vm():
    try:
        if ('faculty' in auth.user_groups.values()) or ('admin' in auth.user_groups.values()):
            owner_id = session.username
            vm_state = 1
        else:
            owner_id = request.vars.faculty
            vm_state = 0

        db.vm_requests.insert(vm_name=request.vars.vm_name, 
                              flavor=request.vars.config,
                              sec_domain=request.vars.sec_domain, 
                              image=request.vars.template,
                              owner=owner_id, 
                              requester=session.username, 
                              purpose=request.vars.purpose,
                              public_ip_required=1 if request.vars.public_ip == 'yes' else 0,
                              extra_storage=request.vars.storage,
                              collaborators=request.vars.collaborators,
                              request_time=int(time.time()),
                              state=vm_state
                              )
        user_email = ldap.fetch_user_info(session.username)['user_email']
        if mailer.send(mailer.MailTypes.VMRequest, user_email):
            db.commit()
            return jsonify()
        else:
            db.rollback()
            raise Exception('Email sending failed')
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))


@auth.requires_login()
def modify_request():
    try:
        db(db.vm_requests.id == request.vars.id).update(
            extra_storage=request.vars.storage,
            public_ip_required=1 if request.vars.public_ip == 'yes' else 0,
            flavor=request.vars.flavor)
        db.commit()
        return jsonify()
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))


@auth.requires_login()
def request_resize():
    try:
        db.resize_requests.insert(vm_name=request.vars.vm_name,
                vm_id=request.vars.vmid,
                new_flavor=request.vars.new_flavor,
                request_time=int(time.time())
                )
        db.commit()
        return jsonify()
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))


def register_user():
    try:
        faculty_privileges = 0
        try:
            faculty_privileges = int(bool(request.vars.chk_faculty_privileges))
        except Exception:
            pass
        db.account_requests.insert(username=request.vars.username,
                userid=request.vars.userid,
                password=request.vars.password,
                email=request.vars.email,
                faculty_privileges=faculty_privileges,
                request_time=int(time.time()),
                approval_status=0
                )
        return jsonify()
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail', message=e.message or str(e.__class__))

@auth.requires_login()
def request_clone():
    try:
        db.clone_requests.insert(
                vm_id=request.vars.vmid,
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
