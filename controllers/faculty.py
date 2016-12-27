import json


# State:0= Requested
# State:1= Faculty Approved
# State:2= Approved/In-queue


@auth.requires_login()
def pending_requests():
    if request.extension in (None, 'html', ''):
        return dict()
    elif request.extension == 'json':
        rows = db((db.vm_requests.state == 0) &
                  (db.vm_requests.owner == session.auth.user.username)).select()
        l = rows.as_list()
        STR = 'public_ip_required'
        for i in l:
            i['flavor'] = flavor_info(i['flavor'])
            i['sec_domain'] = network_name_from_id(i['sec_domain'])
            i['request_time'] = seconds_to_localtime(i['request_time'])
            i[STR] = 'Required' if i[STR] == 1 else 'Not Required'
        return json.dumps({'data': l})


@auth.requires_login()
def pending_requests_list():
    return dict()
