import Baadal
from pprint import pprint
_authurl = 'http://192.168.56.102:35357/v2.0'
_tenant = 'admin'
_username = 'admin'
_password = 'baadal'
conn = Baadal.Connection(_authurl, _tenant, _username, _password)
