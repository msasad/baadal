import time
from gluon.tools import Storage


@auth.requires_login()
def new_vm():
    try:
        if ('faculty' in auth.user_groups.values()) or \
                ('admin' in auth.user_groups.values()):
            owner_id = session.username
            vm_state = 1
        else:
            owner_id = request.vars.faculty
            vm_state = 0

        public_ip_required = 1 if request.vars.public_ip == 'yes' else 0
        db.vm_requests.insert(vm_name=request.vars.vm_name,
                              flavor=request.vars.config,
                              sec_domain=request.vars.sec_domain,
                              image=request.vars.template,
                              owner=owner_id,
                              requester=session.username,
                              purpose=request.vars.purpose,
                              public_ip_required=public_ip_required,
                              extra_storage=request.vars.storage,
                              collaborators=request.vars.collaborators,
                              request_time=int(time.time()),
                              state=vm_state
                              )
        user_email = ldap.fetch_user_info(session.username)['user_email']
        context = Storage()
        context.username = session.username
        context.user_email = user_email
        context.vm_name = request.vars.vm_name
        context.support_email = mail_support

        if mailer.send(mailer.MailTypes.VMRequest, user_email, context):
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
    error_fields = set()
    if userid_in_db(request.vars.userid):
        error_fields.add('userid')
    if email_in_db(request.vars.email):
        error_fields.add('email')
    if not username_is_valid(request.vars.username):
        error_fields.add('username')
    if not userid_is_valid(request.vars.userid):
        error_fields.add('userid')
    if not email_is_valid(request.vars.email):
        error_fields.add('email')
    if len(error_fields):
        raise HTTP(400,body=jsonify(status='fail', fields=list(error_fields)))
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
