from gluon import *


## IMPORTANT Remove hardcoded values before going live
username = 'baadal'
password = 'baadal'
dbhost = '10.237.23.178'
dbname = 'baadal2'
db = DAL('mysql://' + username + ':' + password + '@' + dbhost + '/' + dbname, migrate=False)
db.define_table('vm_requests',
                Field('id','integer'),
                Field('vm_name','string'),
                Field('flavor','integer'),
                Field('sec_domain', 'string'),
                Field('image','string'),
                Field('owner','string'),
                Field('public_ip_required','integer'),
                Field('extra_storage','integer'),
                Field('collaborators','string'),
                Field('request_time','integer')
                )