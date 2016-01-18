@auth.requires_login()
def configs():
    if conn:
        templates = conn.templates()
        values = []
        for t in templates:
            # FIXME if templates are wrapped in Baadal.Templates
            d = t.to_dict()
            values.append({'id':d['id'], 'ram':d['ram'], 'vcpus':d['vcpus']})
        return json.dumps(values)


@auth.requires_login()
def templates():
    """The following metadata needs to be attached to each image
        os-name,
        os-version,
        os-arch,
        disk-size,
        os-edition, (desktop/server)
    """
    if conn:
        images = conn.images()
        values = []
        for i in images:
            # FIXME if images are wrapped in Baadal.Images
            m = i.to_dict()['metadata']
            m['id'] = i.id
            values.append(m)
        return json.dumps(values)


@auth.requires_login()
def networks():
    if conn:
        network_list = conn.networks()
        # logger.debug(network_list)
        values = []
        for i in network_list['networks']:
            if i['name'] != EXTERNAL_NETWORK:
                values.append({'name': i['name'], 'id': i['id']})
        return json.dumps(values)


@auth.requires_login()
def sgroups():
    if conn:
        sgroups = conn.sgroups()
        values = []
        for i in sgroups['security_groups']:
            values.append({'name': i['name'], 'id': i['id']})
        return json.dumps(values)
