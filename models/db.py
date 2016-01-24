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

auth = Auth(db)
auth.define_tables(username=True)
auth.settings.login_methods.append(ldap_auth(mode='custom', username_attrib='cn', custom_scope='subtree',
    server=ldap_host, base_dn=ldap_dn))
auth.settings.create_user_groups = False
auth.settings.login_onaccept = [login_callback]

#auth.settings.login_url = '/baadal/user/login.html'
auth.settings.remember_me_form = False
auth.settings.logout_next = '/baadal/default/user/login'
auth.settings.login_next = '/baadal/user/index'
#auth.settings.on_failed_authorization = '/baadal/default/404.html'
