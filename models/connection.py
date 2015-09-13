import Baadal
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')
authurl = config.get('auth','authurl')
tenant = config.get('auth','tenant')
password = config.get('auth','password')
username = config.get('auth', 'username')
conn = Baadal.Connection(authurl, tenant, username, password)
