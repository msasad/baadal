from gluon.tools import Auth
from gluon.contrib.login_methods.ldap_auth import ldap_auth
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')

dbhost = config.get('database', 'dbhost')
username = config.get('database', 'username')
password = config.get('database', 'password')
dbname = config.get('database', 'database')

ldap_host = config.get('ldap', 'ldap_host')
ldap_dn = config.get('ldap', 'ldap_dn')

db = DAL('mysql://' + username + ':' + password + '@' + dbhost + '/' + dbname, fake_migrate_all=True)
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
        Field('faculty_privileges', 'integer', requires=IS_INT_IN_RANGE(0,1)),
        Field('password', 'string', required=True),
        Field('request_time', 'integer', requires=IS_INT_IN_RANGE(0,1)),
        Field('approval_status', 'integer')
        )

db.define_table('clone_requests',
        Field('id', 'integer'),
        Field('user', 'string', required=True),
        Field('vm_id', 'string', required=True),
        Field('clone_name', 'string'),
        Field('full_clone', 'integer', requires=IS_INT_IN_RANGE(0,1)),
        Field('request_time', 'integer', requires=IS_INT_IN_RANGE(0,1)),
        Field('status', 'integer')
        )

db.define_table('floating_ip_requests',
        Field('id', 'integer'),
        Field('user', 'string', required=True),
        Field('vmid', 'string', required=True),
        Field('request_time', 'integer', requires=IS_INT_IN_RANGE(0,1)),
        Field('status', 'integer')
        )

db.define_table('virtual_disk_requests',
        Field('id', 'integer'),
        Field('user', 'string', required=True),
        Field('vmid', 'string', required=True),
        Field('request_time', 'integer', requires=IS_INT_IN_RANGE(0,1)),
        Field('status', 'integer'),
        Field('disk_size', 'integer')
        )

db.define_table('vm_activity_log',
        Field('id', 'integer'),
        Field('vmid', 'string'),
        Field('user', 'string'),
        Field('task', 'string'),
        Field('time', 'datetime')
        )

auth = Auth(db)
auth.define_tables(username=True)
auth.settings.login_methods.append(ldap_auth(mode='custom', username_attrib='uid',
    custom_scope='subtree', server=ldap_host, base_dn=ldap_dn))
auth.settings.create_user_groups = False
auth.settings.login_onaccept = [login_callback]

#auth.settings.login_url = '/baadal/user/login.html'
auth.settings.remember_me_form = False
auth.settings.logout_next = '/baadal/default/user/login'
auth.settings.login_next = '/baadal/user/index'
#auth.settings.on_failed_authorization = '/baadal/default/404.html'
