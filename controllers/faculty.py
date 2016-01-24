import json

#State:0= Requested
#State:1= Faculty Approved
#State:2= Approved/In-queue

@auth.requires_login()
def pending_requests():
    rows = db((db.vm_requests.state == 0) & (db.vm_requests.owner == session.username)).select()
    l = rows.as_list()
    for i in l:
        i['flavor'] = flavor_info(i['flavor'])
        i['sec_domain'] = network_name_from_id(i['sec_domain'])
        i['request_time'] = seconds_to_localtime(i['request_time'])
        i['public_ip_required'] = 'Required' if i['public_ip_required'] == 1 else 'Not Required'
    return json.dumps({'data': l})
    pass

@auth.requires_login()
def pending_requests_list():
    return dict()

