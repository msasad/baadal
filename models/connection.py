import Baadal
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')
_authurl = config.get('auth', 'authurl')
_tenant = config.get('auth', 'tenant')
_password = config.get('auth', 'password')
_username = config.get('auth', 'username')
conn = Baadal.Connection(_authurl, _tenant, _username, _password)

# FIXME Remove this line
session.username = _username

EXTERNAL_NETWORK = config.get('misc', 'external_network_name')

