import Baadal
import ConfigParser
from BaadalLDAP import BaadalLDAP
from BaadalMailer import BaadalMailer

config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')
_authurl = config.get('auth', 'authurl')
_tenant = config.get('auth', 'tenant')

ldap_host = config.get('ldap', 'ldap_host')
ldap_dn = config.get('ldap', 'ldap_dn')
ldap_base_dn = config.get('ldap', 'ldap_base_dn')
ldap_admin_dn = config.get('ldap', 'ldap_admin_dn')
ldap_admin_password = config.get('ldap', 'ldap_admin_password')

# FIXME Remove this line
EXTERNAL_NETWORK = config.get('misc', 'external_network_name')
