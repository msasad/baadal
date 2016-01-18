
# FIXME Remove hardcoded values before going live
username = 'baadal'
password = 'baadal'
dbhost = '192.168.56.101'
dbname = 'baadal2'
db = DAL('mysql://' + username + ':' + password + '@' + dbhost + '/' + dbname, migrate=False)
db.define_table('vm_requests',
                Field('id', 'integer'),
                Field('vm_name', 'string'),
                Field('flavor', 'string'),
                Field('sec_domain', 'string'),
                Field('image', 'string'),
                Field('owner', 'string'),
                Field('public_ip_required', 'integer'),
                Field('extra_storage', 'integer'),
                Field('collaborators', 'string'),
                Field('request_time', 'integer'),
                Field('purpose', 'string'),
                Field('state', 'integer'),
                )


# authdb = DAL('mysql://' + username + ':' + password + '@' + dbhost + '/' + dbname)
from gluon.tools import Auth
from gluon.contrib.login_methods.ldap_auth import ldap_auth
auth = Auth(db)
auth.define_tables(username=True)
auth.settings.login_methods.append(ldap_auth(mode='cn',
    server='192.168.56.201', base_dn='ou=People,dc=baadal,dc=iitd,dc=ernet,dc=in'))

#auth.settings.login_url = '/baadal/user/login.html'
auth.settings.remember_me_form = False
auth.settings.logout_next = '/baadal/default/user/login'
auth.settings.login_next = '/baadal/user/index'
#auth.settings.on_failed_authorization = '/baadal/default/404.html'
