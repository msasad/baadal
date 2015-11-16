#!/usr/bin/python

import datetime
_EXTERNAL_NETWORK = 'ext-net'
_UNKNOWN_ERROR_MSG = 'Unknown Error'
TIMEZONE = 'Asia/Kolkata'
USAGE_PARAMS = {
                'free_storage': 'free_disk_gb',
                'used_storage': 'local_gb_used',
                'total_storage': 'local_gb',
                'free_memory': 'free_ram_mb',
                'used_memory': 'memory_mb_used',
                'total_memory': 'memory_mb',
                'total_vms': 'running_vms',
                'load_avg': 'current_workload',
                'vcpus': 'vcpus',
                'vcpus_used': 'vcpus_used'
        }

STATUS = {
                'ACTIVE': 'Running',
                'SHUTOFF': 'Shutdown',
                'PAUSED': 'Paused',
                'BUILD': 'Building',
                'ERROR': 'Error'
        }


class Machine:
    def __init__(self, ):
        self.hostname = ""
        self.config = {
                'memory': None,
                'storage': None,
                'extra_storage': None,
                'cpu': None,
                'private_ip': None,
                'public_ip': None
        }


class BaadalVM(object):
    def __init__(self, vmid=None, server=None, conn=None):
        if vmid is not None and server is not None:
            raise BaadalException('Cannot initialise server, please specify either server or id')
        else:
            if str(type(server)).endswith("novaclient.v2.servers.Server'>"):
                self.server = server
                self.__conn = conn

        self.name = self.server.name
        self.id = None
        self.identity = None
        self.hostid = None
        self.vnc_port = None
        self.purpose = None
        self.datastore = None
        self.template_id = None
        self.expiry_date = None
        self.start_time = self.server.__getattr__('OS-SRV-USG:launched_at')
        self.security_domain = None
        self.snapshots = []
        pass

    def attach_disk(self, disk, device_path):
        """

        :param disk: instance of disk to be attached
        :param device_path: path in the system where the disk is to be attached
        :return:
        """
        try:
            self.__conn.nova.volumes.create_server_volume(self.server.id, disk.id, device_path)
            return True
        except Exception as e:
            raise BaadalException(e.message or _UNKNOWN_ERROR_MSG)

    def attach_floating_ip(self, floatingip=None, fixed_address=None):
        if floatingip is None:
            netid = self.__conn.neutron.list_networks(name=_EXTERNAL_NETWORK)['networks'][0]['id']
            floatingip = self.__conn.neutron.create_floatingip(body={'floatingip': {'floating_network_id': netid}})
        floatingipaddress = floatingip['floatingip']['floating_ip_address']
        self.server.add_floating_ip(floatingipaddress, fixed_address)
        pass

    def attach_nic(self, netid):
        # FIXME:
        try:
            self.server.add_fixed_ip(netid)
        except Exception as e:
            raise BaadalException(e.message or _UNKNOWN_ERROR_MSG)
        pass
    
    def clone(self, clone_name=None, clone_type='Full'):
        """
        :param clone_name: name of the newly created clone instance (optional)
        :param clone_type: type of clone Full or Linked, defaults to Full (optional)
        :return:
        """
        # create a snapshot of the  machine
        # create a new vm using the newly created snapshot
        # delete the snapshot
        try:
            clone_name = clone_name or self.server.name + '_clone'
            flavor_id = self.server.flavor['id']
            networks = self.get_networks().keys()
            network_ids = [
                self.__conn.neutron.list_networks(name=network)['networks'][0]['id'] for network in networks]
            nics = [{'net-id': netid for netid in network_ids}]
            snapshot_id = self.server.create_image("temp")
            image = self.__conn.nova.images.find(id=snapshot_id)
            while image.status != 'ACTIVE':
                image = self.__conn.nova.images.find(id=snapshot_id)
                pass
            else:
                clone = self.server.manager.create(clone_name, image,
                                                   self.__conn.nova.flavors.find(id=flavor_id), nics=nics,
                                                   security_groups=networks, meta=self.server.metadata)
                while clone.status != 'ACTIVE':
                    clone = clone.manager.find(id=clone.id)
                else:
                    image.delete()
                    attached_disks = self.get_attached_disks()
                    for i in attached_disks:
                        volid = i['id']
                        if clone_type == 'Full':
                            volume_clone = self.__conn.cinder.volumes.create(i['size'], source_volid=i['id'])
                            volid = volume_clone.id
                            while volume_clone.status != 'available':
                                volume_clone = self.__conn.cinder.volumes.get(volume_clone.id)
                        self.__conn.nova.volumes.create_server_volume(clone.id, volid, i['path'])
            return clone
        except Exception as e:
            raise BaadalException(e.message)
        pass

    def create_snapshot(self, snapshot_name=None):
        try:
            snapshot_name = snapshot_name or self.server.name + "snapshot" + datetime.datetime.now().isoformat()
            snapshot_id = self.server.create_image(snapshot_name)
            return snapshot_id
        except Exception as e:
            raise BaadalException(e)
        pass
    
    def delete(self, ):
        try:
            res = self.server.delete()
            return res
        except Exception as e:
            raise BaadalException(e)
        pass

    def get_attached_disks(self, ):
        volume_ids = self.server.__getattr__('os-extended-volumes:volumes_attached')
        disk_list = []
        for i in volume_ids:
            volume = self.__conn.cinder.volumes.find(id=i['id'])
            attachments_list = volume.attachments
            for entry in attachments_list:
                if entry['server_id'] == self.server.id:
                    devicepath = entry['device']
                    disk_list.append({
                        'size': volume.size,
                        'id': i['id'],
                        'path': devicepath
                        })
                    pass
            pass
        return disk_list

    def get_networks(self, ):
        try:
            return self.server.networks
        except Exception as e:
            raise BaadalException(e)

    def get_snapshots(self):
        try:
            snapshots = []
            all_images = self.__conn.nova.images.list()
            for img in all_images:
                if hasattr(img, 'server') and img.server['id'] == self.server.id:
                    snapshots.append(img)
            return snapshots
        except Exception as e:
            raise BaadalException(e.message or str(e.__class__))

    def get_status(self, ):
        self.refresh_status()
        return STATUS.get(self.server.status, 'Unknown')
        pass

    def get_vnc_console(self, console_type='novnc'):
        return self.server.get_vnc_console(console_type)['console']['url']

    @staticmethod
    def __cmp(x, y):
        import time
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        secondsx = time.mktime(time.strptime(x.created, fmt))
        secondsy = time.mktime(time.strptime(y.created, fmt))
        if secondsx == secondsy:
            return 0
        elif secondsx > secondsy:
            return 1
        else:
            return -1

    def last_snapshot(self, ):
        snapshots = self.get_snapshots()
        snapshots.sort(cmp=self.__cmp, reverse=True)
        return snapshots[0]

    def migrate(self, live=False):
        try:
            if live is True:
                res = self.server.migrate()
            else:
                res = self.server.live_migrate()
            return res
        except Exception as e:
            raise BaadalException(e)
        pass

    def pause(self, ):
        try:
            res = self.server.suspend()
            return res
        except Exception as e:
            raise BaadalException(e)
        pass

    def properties(self):
        server_properties = self.server.to_dict()
        properties = dict()
        properties['id'] = self.server.id
        properties['name'] = self.server.name
        properties['owner'] = ''
        properties['status'] = self.get_status()
        properties['ip-addresses'] = []
        for (network, addresses) in server_properties['addresses'].iteritems():            
            for address in addresses:
                properties['ip-addresses'].append({
                    'network': network, 'address': address['addr'], 'MAC': address['OS-EXT-IPS-MAC:mac_addr']})
            pass
        flavor = self.__conn.nova.flavors.find(id=self.server.flavor['id'])
        # properties['flavor'] = flavor
        properties['status'] = self.get_status()
        properties['memory'] = flavor.__getattr__('ram')
        properties['vcpus'] = flavor.__getattr__('vcpus')
        properties['hostid'] = self.server.hostId
        properties['hostname'] = self.server.__getattr__('OS-EXT-SRV-ATTR:hypervisor_hostname')
        snapshots = self.get_snapshots()
        l = []
        for snapshot in snapshots:
            l.append({'id': snapshot.id, 'created': snapshot.created, 'name': snapshot.name})
        properties['snapshots'] = l
        return properties
        pass

    def reboot(self, soft=True):
        """

        :param soft:
        :return:
        """
        try:
            if soft is True:
                res = self.server.reboot(reboot_type='SOFT')
            else:
                res = self.server.reboot(reboot_type='HARD')
            return res
        except Exception as e:
            raise BaadalException(e)

    def refresh_status(self):
        self.server = self.server.manager.find(id=self.server.id)

    def resume(self, ):
        try:
            res = self.server.resume()
            return res
        except Exception as e:
            raise BaadalException(e)
        pass

    def restore_snapshot(self, snapshot_id, password=None, preserve_ephemeral=False, **kwargs):
        try:
            self.server.rebuild(snapshot_id, password=password, preserve_ephemeral=preserve_ephemeral, **kwargs)
        except Exception as e:
            raise BaadalException(e.message or str(e.__class__))

    def shutdown(self):
        """
        Shutdown the virtual machine
        :return: None
        """

        try:
            self.server.stop()
        except Exception as e:
            raise BaadalException(e)
        pass
        
    def start(self, ):
        """
        starts the virtual machine,
        :return: None
        """

        try:
            self.server.start()
        except Exception as e:
            raise BaadalException(e)
        pass

    def update(self, **kwargs):
        for item, value in kwargs.iteritems():
            self.server.manager.set_meta_item(self.server, item, str(value))
        pass
    pass

    def metadata(self):
        return self.server.metadata


class Connection:
    """
    A wrapper class for objects of novaclient, neutronclient, cinderclient and keystoneclient
    """
    def __init__(self, authurl, tenant_name, username, password):
        from keystoneclient.auth.identity import v2
        from keystoneclient import session
        from novaclient import client
        from neutronclient.neutron import client as nclient
        from cinderclient import client as cclient 
        auth = v2.Password(auth_url=authurl, username=username,
                           password=password, tenant_name=tenant_name)
        sess = session.Session(auth=auth)

        class ConnectionWrapper:
            def __init__(self, nova, cinder, neutron):
                self.nova = nova
                self.neutron = neutron
                self.cinder = cinder
            pass

        self.__auth = auth
        self.__sess = sess
        self.__conn = ConnectionWrapper(client.Client('2', session=sess), cclient.Client('2', session=sess),
                                        nclient.Client('2.0', session=sess))
        del ConnectionWrapper

        self.userid = self.__conn.nova.client.get_user_id()
        self.user_is_project_admin = self.__conn.user_is_project_admin = bool(self.get_user_roles().count('admin'))

        # FIXME Retain these lines during testing only
        self.nova = self.__conn.nova
        self.cinder = self.__conn.cinder
        self.neutron = self.__conn.neutron
        self.auth = auth
        self.sess = sess
        pass

    def get_user_roles(self):
        roles = []
        roles_list = self.__auth.get_access(self.__sess)['user']['roles']
        for entry in roles_list:
            roles.append(str(entry['name']))
        return roles

    def close(self, ):
        del self.__conn
        pass

    def usage(self, attribute_list=None):
        """
        :param attribute_list: optional; list of usage paramenters to fetch
        :return: a dict object representing resource usage of a compute node
        """

        values = {}
        stats = self.__conn.nova.hypervisor_stats.statistics().to_dict()
        attribute_list = attribute_list or USAGE_PARAMS.keys()
        for item in attribute_list:
            values[item] = stats[USAGE_PARAMS[item]]
        return values
        pass

    def baadal_vms(self, all_users=False):
        """
        :param all_users: optional; list VMs belonging to all users in the project, requires admin role
        :return:
        """
        if not self.__conn.nova:
            raise BaadalException('Not connected to openstack nova service')
        try:
            if all_users:
                if not self.user_is_project_admin:
                    raise BaadalException('Access denied! User must be project admin to list all VMs')
                else:
                    serverlist = self.__conn.nova.servers.list()
            else:
                serverlist = self.__conn.nova.servers.findall(user_id=self.userid)
            if serverlist:
                serverlist = [BaadalVM(server=i, conn=self.__conn) for i in serverlist]
            return serverlist or []
        except Exception as e:
            raise BaadalException(e.message or str(e.__class__))
        pass

    def find_baadal_vm(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        if not self.__conn.nova:
            raise BaadalException('Not connected to openstack nova service')
        try:
            baadalvm = self.__conn.nova.servers.find(**kwargs)
            return BaadalVM(server=baadalvm, conn=self.__conn)
        except Exception as e:
            raise BaadalException(e.message)
        pass

    def create_baadal_vm(self, name, image, template, nics, **kwargs):
        """

        :param name:
        :param image:
        :param template:
        :param nics:
        :param kwargs:
        :return:
        """
        """ nics must be None or a list of dictionaries of the format
        {
            net-id : uuid of the network,
            v4-fixed-ip: fixed IPv4 address,
            port-id: uuid of the port if already defined
        }
        """
        if not self.__conn.nova:
            raise BaadalException('Not connected to openstack nova service')
        try:
            sec_group = self._network_name_from_id(nics[0]['net-id'])
            server = self.__conn.nova.servers.create(name, image, template, nics=nics, security_groups=[sec_group],
                                                     **kwargs)
            return BaadalVM(server=server, conn=self.__conn)
        except Exception as e:
            raise BaadalException(e.message)

    def create_volume(self, size, imageref=None, multiattach=False):
        if not self.__conn.cinder:
            raise BaadalException('Not connected to openstack cinder service')
        volume = self.__conn.cinder.volumes.create(size, imageRef=imageref, multiattach=multiattach)
        return volume

    def create_template(self, name, ram, disk, vcpus):
        if not self.__conn.nova:
            raise BaadalException('Not connected to openstack nova service')
        try:
            flavor = self.__conn.nova.flavors.create(name, ram, vcpus, disk)
            return flavor
        except Exception as e:
            raise BaadalException("Could not create flavor" + e.message)
    
    def get_disk_by_id(self, diskid):
        if not self.__conn.cinder:
            raise BaadalException('Not connected to openstack cinder service')
        return self.__conn.cinder.volumes.get(diskid)

    def images(self, ):
        if not self.__conn.nova:
            raise BaadalException('Not connected to openstack nova service')
        try:
            imageslist = self.__conn.nova.images.list()
            return imageslist
        except Exception as e:
            raise BaadalException(e.message)
        pass

    def find_image(self, **kwargs):
        if not self.__conn.nova:
            raise BaadalException('Not connected to openstack nova service')
        try:
            image = self.__conn.nova.images.find(**kwargs)
            return image
        except Exception as e:
            raise BaadalException(e.message)
        pass
   
    def hypervisors(self, name=None, id=None):
        if not self.__conn.nova:
            raise BaadalException('Not connected to openstack nova service')
        if name and id:
            raise BaadalException('Cannot find hypervisor! Please specify either name or Id')
        try:
            if not name and not id:
                hypervisors = self.__conn.nova.hypervisors.list()
            elif name:
                hypervisors = self.__conn.nova.hypervisors.find(hypervisor_hostname=name)
            else:
                hypervisors = self.__conn.nova.hypervisors.find(id=id)
            return hypervisors
        except Exception as e:
            raise BaadalException(e.message or _UNKNOWN_ERROR_MSG)

    def templates(self):
        if not self.__conn.nova:
            raise BaadalException('Not connected to openstack nova service')
        try:
            templates = self.__conn.nova.flavors.list()
            return templates
        except Exception as e:
            raise BaadalException(e.message)
        pass

    def find_template(self, **kwargs):
        if not self.__conn.nova:
            raise BaadalException('Not connected to openstack nova service')
        try:
            template = self.__conn.nova.flavors.find(**kwargs)
            return template
        except Exception as e:
            raise BaadalException(e.message)
        pass
    
    def sgroups(self, ):
        if not self.__conn.neutron:
            raise BaadalException('Not connected to openstack neutron service')
        try:
            sgroups = self.__conn.neutron.list_security_groups()
            return sgroups
        except Exception as e:
            raise BaadalException(e.message)

    def networks(self, ):
        try:
            networks = self.__conn.neutron.list_networks()
            return networks
        except Exception as e:
            raise BaadalException(e.message)
        pass
    pass

    def subnets(self, network_id=None):
        try:
            if network_id:
                subnet_list = self.__conn.neutron.list_subnets(network_id=network_id)
            else:
                subnet_list = self.__conn.neutron.list_subnets()
            return subnet_list
        except Exception as e:
            raise BaadalException(e.message)

    def _network_name_from_id(self, netid):
        netlist = self.networks()['networks']
        for i in netlist:
            if netid == i['id']:
                return i['name']

    def _netid_from_name(self, netname):
        for net in self.networks()['networks']:
            if net['name'] == netname:
                return net['id']

    def create_network(self, network_name, cidr, ip_version=None, dns_name=None):
        try:
            body_sample = {'network': {'name': network_name, 'admin_state_up': True}}
            netw = self.__conn.neutron.create_network(body=body_sample)
            net_dict = netw['network']
            network_id = net_dict['id']
            return network_id
        except Exception as e:
            raise BaadalException(e.message)

    def create_subnet(self, network_id, cidr, ip_version=None, dns_name=None):
        try:
            body_create_subnet = {'subnets': [{'cidr': cidr, 'ip_version': 4, 'network_id': network_id}]}
            subnet = self.__conn.neutron.create_subnet(body=body_create_subnet)
        except Exception as e:
            raise BaadalException(e.message)

    def delete_network(self, network_id):
        try:
            self.__conn.neutron.delete_network(network_id)
        except Exception as e:
            raise BaadalException(e.message)
     
    def create_security_domain(self, sg_name):
        try:
            security_group = {'name': sg_name}
            sg = self.__conn.neutron.create_security_group({'security_group': security_group})
        except Exception as e:
            raise BaadalException(e.message)


class BaadalException(Exception):
    def __init__(self, msg):
        self.message = msg
