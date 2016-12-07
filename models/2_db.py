from gluon.tools import Auth
from gluon.contrib.login_methods.ldap_auth import ldap_auth
import ConfigParser
from gluon import current
from gluon.scheduler import Scheduler
from gluon.contrib.login_methods.oauth20_account import OAuthAccount
import json,simplejson,requests
ADMIN = 'admin'
current.ADMIN = ADMIN
#added to make auth and db objects available in modules
REQUEST_STATUS_POSTED = 0
REQUEST_STATUS_FACULTY_APPROVED = 1
REQUEST_STATUS_PROCESSING = 3
REQUEST_STATUS_APPROVED = 2

config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')

ldap_host = config.get('ldap', 'ldap_host')
ldap_dn = config.get('ldap', 'ldap_dn')

dbhost = config.get('database', 'dbhost')
username = config.get('database', 'username')
password = config.get('database', 'password')
dbname = config.get('database', 'database')

db = DAL('mysql://' + username + ':' + password + '@' + dbhost + '/' + dbname,
#         migrate=True)
         fake_migrate_all=True)
auth = Auth(db)
current.db = db
## configure custom auth tables
auth.settings.table_user_name = 'auth_user'
auth.settings.table_group_name = 'auth_group'
auth.settings.table_membership_name = 'auth_membership'
db.define_table(
            auth.settings.table_user_name,
            Field('first_name', length = 128, default = ''),
            Field('last_name', length = 128, default = ''),
            Field('email', length = 128, unique = True), # required
            Field('username', length = 128, default = '', unique = True),
            Field('password', 'password', length = 512, readable = False, label = 'Password'), # required
            Field('registration_key', length = 512, writable = False, readable = False, default = ''), # required
            Field('reset_password_key', length = 512, writable = False, readable = False, default = ''), # required
            Field('user_id', length = 512, default = ''),
            Field('registration_id', length = 512, writable = False, readable = False, default = ''),
            format = '%(first_name)s %(last_name)s') # required

custom_auth_table = db[auth.settings.table_user_name]
custom_auth_table.first_name.requires =   IS_NOT_EMPTY(error_message = auth.messages.is_empty)
custom_auth_table.last_name.requires =   IS_NOT_EMPTY(error_message = auth.messages.is_empty)
custom_auth_table.password.requires =   IS_NOT_EMPTY(error_message = auth.messages.is_empty)
custom_auth_table.email.requires = [
          IS_EMAIL(error_message = auth.messages.invalid_email),
          IS_NOT_IN_DB(db, custom_auth_table.email)]
auth.settings.table_user = custom_auth_table

auth.settings.table_group = db.define_table(
            auth.settings.table_group_name,
            Field('role', 'string', length = 100, notnull = True, unique = True),
            Field('description', length = 255, default = ''),
            format = '%(role)s')

auth.settings.table_membership = db.define_table(
            auth.settings.table_membership_name,
            Field('user_id', db.auth_user),
            Field('group_id', db.auth_group),
            primarykey = ['user_id', 'group_id'])

db.define_table('vm_requests',
                Field('id', 'integer'),
                Field('vm_name', 'string'),
                Field('flavor', 'string'),
                Field('sec_domain', 'string'),
                Field('image', 'string'),
                Field('owner', 'string'),
                Field('requester', 'string'),
                Field('public_ip_required', 'integer'),
                Field('extra_storage', 'integer'),
                Field('collaborators', 'string'),
                Field('request_time', 'integer'),
                Field('purpose', 'string'),
                Field('state', 'integer'),
                )

db.define_table('resize_requests',
                Field('id', 'integer'),
                Field('vmname', 'string'),
                Field('user', 'string'),
                Field('vm_id', 'string'),
                Field('new_flavor', 'string'),
                Field('request_time', 'integer'),
                Field('status', 'integer')
                )

db.define_table('account_requests',
                Field('id', 'integer'),
                Field('username', 'string', required=True),
                Field('userid', 'string', required=True, unique=True),
                Field('email', 'string', requires=IS_EMAIL()),
                Field('faculty_privileges', 'integer',
                      requires=IS_INT_IN_RANGE(0, 1)),
                Field('password', 'string', required=True),
                Field('request_time', 'integer',
                      requires=IS_INT_IN_RANGE(0, 1)),
                Field('approval_status', 'integer')
                )

db.define_table('clone_requests',
                Field('id', 'integer'),
                Field('user', 'string', required=True),
                Field('vm_id', 'string', required=True),
                Field('clone_name', 'string'),
                Field('full_clone', 'integer', requires=IS_INT_IN_RANGE(0, 1)),
                Field('request_time', 'integer',
                      requires=IS_INT_IN_RANGE(0, 1)),
                Field('status', 'integer')
                )

db.define_table('floating_ip_requests',
                Field('id', 'integer'),
                Field('user', 'string', required=True),
                Field('vmid', 'string', required=True),
                Field('request_time', 'datetime', default=request.now),
                Field('status', 'integer')
                )

db.define_table('virtual_disk_requests',
                Field('id', 'integer'),
                Field('user', 'string', required=True),
                Field('vmid', 'string', required=True),
                Field('request_time', 'datetime'),
                Field('status', 'integer'),
                Field('disk_size', 'integer')
                )

db.define_table('vm_activity_log',
                Field('id', 'integer'),
                Field('vmid', 'string'),
                Field('user', 'string'),
                Field('task', 'string'),
                Field('time', 'datetime', default=request.now),
                Field('remarks', 'string')
                )

auth = Auth(db)
auth.define_tables(username=True)
auth.settings.login_methods.append(ldap_auth(mode='custom',
                                   username_attrib='uid',
                                   custom_scope='subtree',
                                   server=ldap_host, base_dn=ldap_dn))
auth.settings.create_user_groups = False
#auth.settings.login_onaccept = [login_callback]

auth.settings.remember_me_form = False
auth.settings.logout_next = '/baadal/default/user/login'
auth.settings.login_next = '/baadal/user/index'

scheduler = Scheduler(db)
