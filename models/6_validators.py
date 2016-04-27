from gluon import validators


def validate_registration_form(vars):
    """
    Validates the user registration form
    which includes the following fields
    username, userid, email, password, password_repeat
    params: request.vars
    returns: list of fields for which validation failed
    """
    fields = []
    if not userid_is_valid(vars.userid):
        fields.append('userid')
    if not username_is_valid(vars.username):
        fields.append('username')
    if not email_is_valid(vars.email):
        fields.append('email')
    if not password_is_valid(vars.password, vars['password-repeat']):
        fields.append('password')
        fields.append('password-repeat')
    return fields


def userid_is_valid(userid):
    valid = True
    length = len(userid)
    validator = validators.IS_IN_DB(db, db.account_requests.userid)
    valid = valid and validator(userid)[1] is not None and (4 <= length <= 12)
    validator = validators.IS_ALPHANUMERIC()
    valid = valid and validator(userid)[1] is None
    return valid


def username_is_valid(username):
    return validators.re.match(r'^[A-Za-z][A-Za-z ]{2,10}[A-Za-z]$',
                               username) is not None


def email_is_valid(email):
    valid = True
    validator = validators.IS_EMAIL(email)
    valid = valid and validator(email)[1] is None
    validator = validators.IS_IN_DB(db, db.account_requests.email)
    valid = valid and validator(email)[1] is not None
    return valid


def password_is_valid(password, password_repeat):
    return len(password) > 6 and (password == password_repeat)


def validate_vm_request_form(vars):
    fields = []
    if not vmname_is_valid(vars.vm_name):
        fields.append('vm_name')
    if not template_is_valid(vars.template):
        fields.append('template')
    if not config_is_valid(vars.config):
        fields.append('config')
    if not security_domain_is_valid(vars.sec_domain):
        fields.append('sec_domain')
    if not storage_is_valid(vars.storage):
        fields.append('storage')
    if not purpose_is_valid(vars.purpose):
        fields.append('purpose')
    if not public_ip_is_valid(vars.public_ip):
        fields.append('public_ip')
    if not collaborators_is_valid(vars.collaborators):
        fields.append('collaborators')
    if not faculty_is_valid(vars.faculty):
        fields.append('faculty')
    return fields


def vmname_is_valid(vm_name):
    return validators.re.match(r'^[A-Za-z][A-Za-z_\-0-9]{2,10}[A-Za-z0-9]$',
                               vm_name) is not None


def template_is_valid(template):
    # templates in Baadal are called images in Openstack
    conn = Baadal.Connection(_authurl, _tenant, session.username,
                             session.password)
    templates = [i.id for i in conn.images()]
    conn.close()
    return template in templates


def config_is_valid(config):
    # config in Baadal are called flavors/templates in Openstack
    conn = Baadal.Connection(_authurl, _tenant, session.username,
                             session.password)
    configs = [c.id for c in conn.templates()]
    conn.close()
    return config in configs


def security_domain_is_valid(sec_domain):
    # security domains Baadal are isolated networks in Openstack
    conn = Baadal.Connection(_authurl, _tenant, session.username,
                             session.password)
    networks = []
    network_list = conn.networks()
    for i in network_list['networks']:
        if i['name'] != EXTERNAL_NETWORK:
            networks.append(i['id'])
    return sec_domain in networks


def storage_is_valid(storage):
    validator = validators.IS_INT_IN_RANGE(0, None)
    return validator(storage)[1] is None


def purpose_is_valid(purpose):
    valid = True
    return valid


def public_ip_is_valid(public_ip):
    return public_ip in ('yes', 'No')


def collaborators_is_valid(collaborators):
    valid = True
    return valid


def faculty_is_valid(faculty):
    valid = True

    return valid
    pass


def validate_subnet_form(vars):
    fields = []
    if not subnet_name_is_valid(vars.subnet_name):
        fields.append('subnet-name')
    if not cidr_is_valid(vars.cidr):
        fields.append('cidr')
    if not nameservers_is_valid(vars.nameservers):
        fields.append('nameservers')
    if not allocation_pool_is_valid(vars.allocation_pool):
        fields.append('allocation-pool')
    if not gateway_ip_is_valid(vars.gateway_ip):
        fields.append('gateway-ip')
    if not static_routes_is_valid(vars.static_routes):
        fields.append('static-routes')
    if not ip_version_is_valid(vars.ip_version):
        fields.append('ip-version')
    return fields


def subnet_name_is_valid(subnet_name):
    return username_is_valid(subnet_name)


def cidr_is_valid(cidr):
    re = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|'\
            '[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|'\
            '3[0-2]))$'
    return validators.re.match(re, cidr) is not None


def nameservers_is_valid(nameservers):
    if nameservers == '':
        return True
    valid = True
    nslist = nameservers.translate(None, ' ').split(',')
    validator = IS_IPV4()
    for ns in nslist:
        if validator(ns)[1] is not None:
            valid = False
            break
    return valid


def allocation_pool_is_valid(allocation_pool):
    if allocation_pool == '':
        return True
    valid = True
    try:
        allocation_pool = request.vars.allocation_pool.\
            translate(None, ' ').split('-')
        if IS_IPV4(allocation_pool[0])[1] is not None or \
        IS_IPV4(allocation_pool[1])[1] is not None:
            valid = False
    except:
        valid = False
    return valid


def gateway_ip_is_valid(gateway_ip):
    try:
        return gateway_ip == '' or IS_IPV4(gateway_ip)[1] is None
    except:
        return False


def static_routes_is_valid(static_routes):
    if static_routes == '':
        return True
    valid = True
    try:
        static_routes = str_to_route_list(static_routes)
        for route in static_routes:
            if IS_IPV4(route['destination'])[1] is not None or \
            IS_IPV4(route['nexthop'])[1] is not None:
                valid = False
                break
    except:
        valid = False
    return valid


def ip_version_is_valid(ip_version):
    return ip_version in [4, 6, '4', '6']
