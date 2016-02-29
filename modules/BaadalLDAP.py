#!/bin/env python

import ldap

class BaadalLDAP(object):
    def __init__(self, ldap_host, base_dn, admin_dn, admin_passwd):
        self.l = ldap.open(ldap_host)
        self.l.simple_bind(admin_dn, admin_passwd)
        self.base_dn = base_dn

    def fetch_all_users(self, enabled_users_only=True):
        pass

    def add_user(self, username, userid, password, user_is_faculty=False, email=None,sn=None, user_is_enabled=True):
        # TODO: Hash password before storing
        ou = 'People'
        enabled_user_group = 'cn=enabled_users,ou=Groups,%s' % self.base_dn
        faculty_group = 'cn=faculties,ou=Groups,%s' % self.base_dn
        user_dn = 'uid=%s,ou=%s,%s' % (userid, ou, self.base_dn)
        user_attributes = [('cn', [username]), ('userPassword', [password]),('objectClass',['top','account','extensibleObject'])]
        self.l.add_s(user_dn, user_attributes)
        if user_is_enabled:
            # TODO: add user to enabled users group
            attributes = [(ldap.MOD_ADD, 'member', user_dn)]
            self.l.modify(enabled_user_group, attributes)
        
        if user_is_faculty:
            self.grant_faculty_role(user_dn)

    def modify_user(self,):
        pass

    def delete_user(self, user_dn):
        self.l.delete_s(user_dn)

    def grant_faculty_role(self, user_dn):
        faculty_group = 'cn=faculties,ou=Groups,%s' % self.base_dn
        attributes = [(ldap.MOD_ADD, 'member', user_dn)]
        self.l.modify_s(faculty_group, attributes)

    def revoke_faculty_role(self, user_dn):
        faculty_group = 'cn=faculties,ou=Groups,%s' % self.base_dn
        attributes = [(ldap.MOD_DELETE, 'member', user_dn)]
        self.l.modify_s(faculty_group, attributes)

    def grant_user_roles(self, user_dn, project_name, role_name):
        pass

    def fetch_user_info(self, user_id):
        result = self.l.search_s(self.base_dn, ldap.SCOPE_SUBTREE, 'uid='+user_id)
        if not result:
            return False
        try:
            user_info = dict()
            user_info['user_dn'] = result[0][0]
            user_info['user_name'] = result[0][1]['cn'][0]
            user_info['user_email'] = result[0][1]['email'][0]
            user_info['user_id'] = result[0][1]['uid'][0]
            return user_info
        except:
            return False
