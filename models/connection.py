import Baadal
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')
_authurl = config.get('auth', 'authurl')
_tenant = config.get('auth', 'tenant')

# FIXME Remove this line
EXTERNAL_NETWORK = config.get('misc', 'external_network_name')

