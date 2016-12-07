#!/bin/env python
from userAuth import update_user_info
import MySQLdb as mdb
import os
import ldap
import logging
import Baadal
import ConfigParser
logger = logging.getLogger("web2py.app.baadal")
#from 1_auth import update_user_info

config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')
_authurl = config.get('auth', 'authurl')
_tenant = config.get('auth', 'tenant')

class BaadalLDAP(object):

    def __init__(self, ldap_host, base_dn, admin_dn, admin_passwd):
        self.l = ldap.open(ldap_host)
        self.l.simple_bind(admin_dn, admin_passwd)
        self.base_dn = base_dn

    def fetch_all_users(self, enabled_users_only=True):
        pass

    def add_user(self, username, userid, password, email, user_is_faculty=False,
                 sn=None, user_is_enabled=True):
        # TODO: Hash password before storing
        ou = 'People'
        enabled_user_group = 'cn=enabled_users,ou=Groups,%s' % self.base_dn
        user_dn = 'uid=%s,ou=%s,%s' % (userid, ou, self.base_dn)
        user_attributes = [('email', [email]), ('cn', [username]),
                           ('userPassword', [password]),
                           ('objectClass', ['top', 'account', 'extensibleObject'])]
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

    def check_valid_user(self, user_id):
        logger.debug("user id is " + str(user_id))
        new_db=mdb.connect("10.237.22.50","root","baadal","baadal")
        n_db=new_db.cursor()
        n_db.execute("select username,email,user_id from auth_user where username= %s",user_id)
        result=n_db.fetchall()
        logger.debug("data value is : " +str(result))
        user_info = dict()
        n_db.close()
        new_db.close()
        if len(result)== 0:
                return False
        else :
                return True



    def fetch_user_info(self, user_id):
        #result = self.l.search_s(
        #    self.base_dn, ldap.SCOPE_SUBTREE, 'uid=' + user_id)
        #if not result:
        #    return False
        logger.debug("user id is " + str(user_id))
        new_db=mdb.connect("10.237.22.50","root","baadal","baadal")
        n_db=new_db.cursor()
        n_db.execute("select username,email,user_id from auth_user where username= %s",user_id)
        result=n_db.fetchall()
        logger.debug("data value is : " +str(result))
        user_info = dict()
        n_db.close()
        new_db.close()
        if len(result)== 0:
              logger.debug("inside if part ")
              my_user=result
              f = os.popen('openssl rand -hex 10')
              token = f.read()
              token = token.split("\n")
              token=token[0]
              logger.debug("token is : " + str(token))
              conn = Baadal.Connection(_authurl, _tenant,'e7221625e0c04660b22179605e8f6c52','baadal')
              my_user = conn.users_create(user_id,token,_tenant)
              logger.debug("my user is : " + str(my_user))
              update_user_info(user_id,my_user,token)
              logger.debug("after user info !!!!!!!!!!!!!!!!!! ")
              value = conn.add_user_role(my_user, _tenant, 'user')
              user_info['user_name'] = user_id
              user_info['user_id'] = my_user
              user_info['user_email'] = user_id + "@cse.iitd.ac.in"
        else:
            logger.debug("inside try block ")
            #user_info['user_dn'] = result[0][0]
            user_info['user_name'] = result[0][0]
            user_info['user_email'] = result[0][1]
            user_info['user_id'] = result[0][2]
            logger.debug("user_info is : " + str(user_info))
        return user_info
        #except:
        #    return False

    def user_is_faculty(self, user_id):
        logger.debug("inside user_is_faculty user id is : " + str(user_id))
        _role_list = "" 
        #faculty_group = 'cn=faculties,ou=Groups,%s' % self.base_dn
        #query = '(member=uid=%s,ou=People,%s)' % (user_id, self.base_dn)
        #result = self.l.search_s(self.base_dn, ldap.SCOPE_SUBTREE, query,
        #                         attrlist=['dn'])
        #group_list = [i[0] for i in result]
        #return group_list.__contains__(faculty_group)
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read('/etc/baadal/baadal.conf')
        user_list = config.get("GENERAL_CONF","faculty_uid")
        logger.debug("user list is " + str(user_list))
        if len(user_id) ==0:
           logger.debug("inside size check block")
           return False
        elif user_id in user_list:
           _role_list='FACULTY'
           logger.debug("inside if block user is faculty")
           #return _role_list
           return True
        else:
           logger.debug("inside else block user is faculty")
           return False
