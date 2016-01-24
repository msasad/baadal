def login():
  pass

def login_callback(form):
    if auth.is_logged_in():
        user_name = auth.user.username
        if db.auth_user(username = user_name)['last_name'] == "":
            user_info = fetch_ldap_user(user_name)
            if user_info:
                update_user_info(user_info)
            else:
                logger.error('Unable To Update User Info!!!')

def fetch_ldap_user(username):

    ldap_url = config.get('ldap', 'ldap_host')
    base_dn = config.get('ldap', 'ldap_dn')

    import ldap
    try:
        l = ldap.open(ldap_url)
        l.protocol_version = ldap.VERSION3    
    except ldap.LDAPError, e:
        logger.error(e)
        return None

    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None
    searchFilter = "cn="+username
    user_info={'user_name':username}
    user_info['email'] = None
    user_info['last_name'] = ''

    try:
        ldap_result_id = l.search(base_dn, searchScope, searchFilter, retrieveAttributes)  
        while 1:
            result_type, result_data = l.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    for name,attrs in result_data:
                        for k,vals in attrs.items():
                            if k == 'cn':
                                name_lst = vals[0].split(' ')
                                user_info['first_name'] = name_lst[0]
                                if len(name_lst) == 2:
                                    user_info['last_name'] = name_lst[1]
                                elif len(name_lst) > 2:
                                    user_info['last_name'] = vals[0][vals[0].index(' '):].lstrip()

        #TODO:FIX finding group of user
        if username in ['admin']:
            user_info['roles'] = ['admin']
        elif username in ['new_user']:
            user_info['roles'] = ['faculty']
        else: 
            user_info['roles'] = ['user']

        if user_info['last_name'] == '':
            user_info['last_name'] = 'user'

    except ldap.LDAPError, e:
        logger.error(e)

    logger.info(user_info)
    if 'first_name' in user_info:
        return user_info
    else: 
        return None


def update_user_info(user_info):

    user_name = user_info['user_name']
    user = db(db.auth_user.username == user_name).select().first()
    
    db(db.auth_user.username==user_name).update(first_name = user_info['first_name'], 
                                                           last_name = user_info['last_name'], 
                                                           email = user_info['email'])
    add_or_update_auth_memberships(user.id, user_info['roles'])


def add_or_update_auth_memberships(user_id, roles):

    current_roles = db((user_id == db.auth_membership.user_id) 
                               & (db.auth_membership.group_id == db.auth_group.id)).select(db.auth_group.role).as_list()

    logger.info("users current roles: %s", current_roles)
    if current_roles != roles:
        db(db.auth_membership.user_id == user_id).delete()
        for role in roles:
            add_membership(user_id, role)

def add_membership(_user_id, role):
    #Find the group_id for the given role
    _group_id = db.auth_group(role=role)['id']
    if _group_id !=0:
        db.auth_membership.insert(user_id=_user_id,group_id=_group_id)
        

