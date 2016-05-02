@auth.requires_login()
def configs():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        if conn:
            templates = conn.templates()
            values = []
            for t in templates:
                # FIXME if templates are wrapped in Baadal.Templates
                d = t.to_dict()
                values.append({
                    'id': d['id'],
                    'ram': d['ram'],
                    'vcpus': d['vcpus']
                })
            return json.dumps(values)
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail', message=e.message)
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires_login()
def templates():
    """The following metadata needs to be attached to each image
        os-name,
        os-version,
        os-arch,
        disk-size,
        os-edition, (desktop/server)
    """
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        if conn:
            images = conn.images(image_type='template')
            values = []
            for i in images:
                # FIXME if images are wrapped in Baadal.Images
                m = i.to_dict()['metadata']
                m['id'] = i.id
                values.append(m)
            return json.dumps(values)
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail', message=e.message)
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires_login()
def networks():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        if conn:
            network_list = conn.networks()
            # logger.debug(network_list)
            values = []
            for i in network_list['networks']:
                if i['name'] != EXTERNAL_NETWORK:
                    values.append({'name': i['name'], 'id': i['id']})
            return json.dumps(values)
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail', message=e.message)
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires_login()
def snapshots():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        if conn:
            vm = conn.find_baadal_vm(id=request.vars.vmid)
            snapshots = vm.get_snapshots()
            l = []
            for snapshot in snapshots:
                l.append({'id': snapshot.id, 'created': snapshot.created,
                          'name': snapshot.name})
            return jsonify(data={'snapshots':l})
    except Exception as e:
        logger.exception(e)
        return jsonify(status='fail', message=e.message)
    finally:
        try:
            conn.close()
        except:
            pass


@auth.requires_login()
def sgroups():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        if conn:
            sgroups = conn.sgroups()
            values = []
            for i in sgroups['security_groups']:
                values.append({'name': i['name'], 'id': i['id']})
            return json.dumps(values)
    except Exception as e:
        logger.error(e.message)
        return jsonify(status='fail', message=e.message)
    finally:
        try:
            conn.close()
        except NameError:
            pass
