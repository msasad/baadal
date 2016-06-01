def login():
    pass


def login_callback(form):
    if auth.is_logged_in():
        user_name = auth.user.username
        if db.auth_user(username=user_name)['last_name'] == "":
            user_info = ldap.fetch_user_info(user_name)
            logger.info(user_info)
            if user_info:
                update_user_info(user_info)
            else:
                logger.error('Unable To Update User Info!!!')


def update_user_info(user_info):
    user_id = user_info['user_id']
    user = db(db.auth_user.username == user_id).select().first()
    user_name = user_info['user_name']
    user_name_list = user_name.split(' ')
    if(len(user_name_list) < 2):
        user_name_list.append('User')
    db(db.auth_user.username == user_id).update(first_name=user_name_list[0],
                                                           last_name=user_name_list[1],
                                                           email=user_info['user_email'])
    add_or_update_auth_memberships(user.id, user_info['user_dn'])


def add_or_update_auth_memberships(user_id, user_dn):

    current_roles = db((user_id == db.auth_membership.user_id) &
                       (db.auth_membership.group_id == db.auth_group.id)).\
                        select(db.auth_group.role).as_list()

    logger.info("users current roles: %s", current_roles)
    roles = [{'role':'user'}]
    if('uid=faculty' in user_dn):
        roles.append({'role':'faculty'})
    logger.info("users new roles: %s", roles)
    if current_roles != roles:
        db(db.auth_membership.user_id == user_id).delete()
        for role in roles:
            add_membership(user_id, role['role'])


def add_membership(_user_id, role):
    # Find the group_id for the given role
    _group_id = db.auth_group(role=role)['id']
    if _group_id != 0:
        db.auth_membership.insert(user_id=_user_id, group_id=_group_id)
