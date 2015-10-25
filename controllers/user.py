def index():
  return dict()

def request():
  return dict()

def login():
  return dict()

def my_vms():
    import json
    vms = conn.baadalVMs()
    response = list()
    for vm in vms:
        response.append(vm.properties())

    return json.dumps({'data' : response})

