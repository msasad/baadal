#!/usr/bin/python

import datetime
_EXTERNAL_NETWORK = 'ext-net'
_UNKNOWN_ERROR_MSG = 'Unknown Error'


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
    def __init__(self, id=None, server=None, conn=None):
        if id is not None and server is not None:
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

    def attachDisk(self, disk, device_path):
        """
        attach a disk to a Virtual Machine
        params:
            disk: instance of disk to be attached
            device_path: path in the system where the disk is to be attached
        return: 
        """

        # try:
        self.__conn['nova'].volumes.create_server_volume(self.server.id, disk.id, device_path)
        return True
        # except Exception as e:
        # debug.log(e)
        raise BaadalException(e.message or _UNKNOWN_ERROR_MSG)
        # return False
        # pass

    def attachFloatingIP(self, floatingip=None, fixed_address=None):
        if floatingip is None:
            netid = self.__conn['neutron'].list_networks(name=_EXTERNAL_NETWORK)['networks'][0]['id']
            floatingip = self.__conn['neutron'].create_floatingip(body={'floatingip': {'floating_network_id': netid}})
            floatingipaddress = floatingip['floatingip']['floating_ip_address']
            pass
        self.server.add_floating_ip(floatingipaddress, fixed_address)
        pass

    def attachNIC(self, netid):
        try:
            self.server.add_fixed_ip(netid)
        except Exception as e:
             raise BaadalException(e.message or _UNKNOWN_ERROR_MSG)   
        pass
    
    def clone(self, clone_name=None, clone_type='Full'):
        """
        create clone of the selected Virtual Machine
        params:
            clone_name: name of the new clone VM to be created (optional),
            an automatically generated name is used if clone_name is not
            supplied
        return:
        """

        # create a snapshot of the  machine
        # create a new vm using the newly created snapshot
        # delete the snapshot
        try:
            clone_name = clone_name or self.server.name + '_clone'
            flavor_id = self.server.flavor['id']
            networks = self.getNetworks().keys()
            network_ids = [self.__conn['neutron'].list_networks(name=network)['networks'][0]['id'] for network in networks]
            nics = [{'net-id': netid for netid in network_ids}]
            snapshot_id = self.server.create_image("temp")
            image = self.__conn['nova'].images.find(id=snapshot_id)
            while image.status != 'ACTIVE':
                image = self.__conn['nova'].images.find(id=snapshot_id)
                pass
            else:
                clone = self.server.manager.create(clone_name, image,
                                                   self.__conn['nova'].flavors.find(id=flavor_id), nics=nics,
                                                   security_groups=networks, meta=self.server.metadata)
                while clone.status != 'ACTIVE':
                    clone = clone.manager.find(id=clone.id)
                else:
                    image.delete()
                    attached_disks = self.getAttachedDisks()
                    for i in attached_disks:
                        volid = i['id']
                        if clone_type == 'Full':
                            volume_clone = self.__conn['cinder'].volumes.create(i['size'], source_volid=i['id'])
                            volid = volume_clone.id
                        while volume_clone.status != 'available':
                            volume_clone = self.__conn['cinder'].volumes.get(volume_clone.id)
                        else:
                            self.__conn['nova'].volumes.create_server_volume(clone.id, volid, i['path'])
            return clone
        except Exception as e:
            # self.__conn['nova'].images.delete(snapshot_id)
            raise BaadalException(e.message)
        pass

    def createSnapshot(self, snapshot_name=None):
        try:
            snapshot_name = snapshot_name or self.server.name + "snapshot" + datetime.datetime.now().isoformat()
            snapshot_id = self.server.create_image(snapshot_name)
            # snapshot_image = self.__conn['nova'].findImage()
            return snapshot_id
            # return Snapshot(snapshot, self.server)
        except Exception as e:
            # debug.log(e)
            raise BaadalException(e)
        pass
    
    def delete(self, ):
        try:
            res = self.server.delete()
            return res
        except Exception as e:
            # debug.log(e)
            raise BaadalException(e)
        pass

    def getAttachedDisks(self, ):
        volume_ids = self.server.__getattr__('os-extended-volumes:volumes_attached')
        disk_list = []
        for i in volume_ids:
            volume = self.__conn['cinder'].volumes.find(id=i['id'])
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

    def getNetworks(self, ):
        try:
            return self.server.networks
        except Exception as e:
            raise BaadalException(e)

    def getStatus(self, ):
        STATUS = {
                'ACTIVE': 'Running',
                'SHUTOFF': 'Shutdown',
                'PAUSED': 'Paused',
                'BUILD': 'Building',
                'ERROR': 'Error'
        }
        self.refreshStatus()
        return STATUS.get(self.server.status, 'Unknown')
        pass

    def getVNCConsole(self, console_type='novnc'):
        return self.server.get_vnc_console(console_type)['console']['url']

    def getXml(self, ):
        return self.server.to_dict()
        pass

    def lastSnapshot(self, ):
        # get the last snapshot of the current VM or return None if no snapshots found
        # usedb
        pass

    def migrate(self, target_host, live=False):
        try:
            if live is True:
                res = self.server.migrate(target_host)
            else:
                res = self.server.live_migrate(target_host)
            return res
        except Exception as e:
            # debug.log(e)
            raise BaadalException(e)
        pass

    def pause(self, ):
        try:
            res = self.server.suspend()
            return res
        except Exception as e:
            # debug.log(e)
            raise BaadalException(e)
        pass

    def properties(self):
        """
        fetch all properties of a VM to show in the front end.
        Name, Owner, Organization, Private IP, Host, Memory, vCPUs, Storage, Status
        """
        
        server_properties = self.server.to_dict()
        properties = dict()
        properties['id'] = self.server.id
        properties['name'] = self.server.name
        properties['owner'] = ''
        properties['status'] = self.getStatus()
        properties['ip-addresses'] = []
        for (network, addresses) in server_properties['addresses'].iteritems():            
            for address in addresses:
                properties['ip-addresses'].append({'network': network, 'address': address['addr'], 'MAC': address['OS-EXT-IPS-MAC:mac_addr']})
            pass
        flavor = self.__conn['nova'].flavors.find(id=self.server.flavor['id'])
        # properties['flavor'] = flavor
        properties['status'] = self.getStatus()
        properties['memory'] = flavor.__getattr__('ram')
        properties['vcpus'] = flavor.__getattr__('vcpus')
        return properties
        pass

    def reboot(self, soft=True):
        """
        reboot the Virtual Machine
        params:
            soft: bool, True for soft reboot, False for hard reboot, default True
        return: None
        """
        try:
            if soft is True:
                res = self.server.reboot(reboot_type='SOFT')
            else:
                res = self.server.reboot(reboot_type='HARD')
            return res
        except Exception as e:
            # debug.log(e)
            raise BaadalException(e)

    def refreshStatus(self):
        # refresh connection to a modified VM
        self.server = self.server.manager.find(id=self.server.id)

    def resume(self, ):
        try:
            res = self.server.resume()
            return res
        except Exception as e:
            # debug.log(e)
            raise BaadalException(e)
        pass

    def revertSpanshot(self, snapshot_id):
        #  usedb
        pass

    def shutdown(self, force=False):
        """
        shutdown the Virtual Machine
        params:
            force: bool, True for forced shutdown, False for graceful shutdown, default False
        return: None
        """

        try:
            self.server.stop()
        except Exception as e:
            # debug.log(e)
            raise BaadalException(e)
        pass
        
    def start(self, ):
        """
        starts the Vritual Machine,
        params: None
        return: None
        """

        try:
            self.server.start()
        except Exception as e:
            # debug.log(e)
            raise BaadalException(e)
        pass

    def update(self, **kwargs):
        # update metadata/config
        for item, value in kwargs.iteritems():
            self.server.manager.set_meta_item(self.server, item, str(value))
        pass
    pass

    """def __getattr__(self, attr):
        if attr == None:
            return self
        if attr is None:
            return self
        if attr == 'status':
            return self.getStatus()
        if attr == 'attacheddisks':
            return self.attachedDisks()
        if attr == 'lastsnapshot':
            return self.lastSnapshot()
        else:
            raise AttributeError
    """


class Image:
    def __init__(self, image):
        self.__image = image
        self.type = None
        pass
    
    def set_metadata(self, prop, value):
        try:
            self.__image.manager.set_meta(self.__image, {prop:value})
        except AttributeError:
            pass
        finally:
            self.__update()

    def delete(self):
        pass
    
    def get_meta(self):
        return self.__image.metadata
    
    def __update(self):
        self.__image = self.__image.manager.get(self.__image.id)
    pass


class Disk:
    def __init__(self, ):
        pass
        
    def attachTo(self, vm, device_path):
        try:
            self.__conn['cinder'].volumes.create_server_volume(vm.id, self.id, device_path)
        except Exception as e:
            # debug.log(e)
            raise BaadalException("Failed to attach disk id " + self.id + "to" + vm.id + e)
        pass
    
    def delete(self):
        pass
    
    pass


class Snapshot:
    def __init__(self, snapshot_name, vm ):
        self.vm_id = vm.id
        self.datastore_id = None
        self.name = snapshot_name
        self.type = None
        self.path = None
        self.timepath = None
        pass

    def delete(self, ):
        pass

    pass


class Template:
    def __init__(self, ):
        self.id = None
        self.name = None
        self.os = {
            'os': None,
            'name': None,
            'type': None,
            'edition': None
        } 
        self.arch = None
        self.hdd = None
        self.type = None
        self.tag = None
        self.datastore = None
        self.owner = None
        self.is_active = None


class HypervisorHost(Machine):
    def __init__(self, ):
        self.category = None
        self.status = None
        self.slot = None
        self.rack = None
        self.hosttype = None
        pass
    pass


class Connection:
    def __init__(self, authurl, tenant_name, username, password):
        from keystoneclient.auth.identity import v2
        from keystoneclient import session
        from novaclient import client
        from neutronclient.neutron import client as nclient
        from cinderclient import client as cclient 
        auth = v2.Password(auth_url=authurl, username=username,
                           password=password, tenant_name=tenant_name)
        sess = session.Session(auth=auth)
        self.__conn = dict()
        self.__conn['nova'] = client.Client('2', session=sess)
        self.__conn['cinder'] = cclient.Client('2', session=sess)
        self.__conn['neutron'] = nclient.Client('2.0', session=sess)

        # Below lines to retained while testing only
        self.nova = self.__conn['nova']
        self.cinder = self.__conn['cinder']
        self.neutron = self.__conn['neutron']
        # self.__cinder = cclient.Client("2", session=sess)
        # self.__conn = client.Client("2", session=sess)
        pass

    def close(self, ):
        pass

    def usage(self, attribute_list=None):
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
        values = {}
        stats = self.__conn['nova'].hypervisor_stats.statistics().to_dict()
        attribute_list = attribute_list or USAGE_PARAMS.keys()
        for item in attribute_list:
            values[item] = stats[USAGE_PARAMS[item]]
        return values
        pass

    def baadalVMs(self, ):
        # return a list of VMs running on the host
        try:
            serverList = self.__conn['nova'].servers.list()
            serverList = [ BaadalVM(server=i, conn=self.__conn) for i in serverList ]
            return serverList
        except Exception as e:
            raise BaadalException(e.message)
            
        # wrap each object of the list of novaclient.v2.servers.Server objects into
        # a list of BaadalVM objects and return it
        pass

    def findBaadalVM(self, **kwargs):
        try:
            baadalVM = self.__conn['nova'].servers.find(**kwargs)
            return BaadalVM(server=baadalVM, conn=self.__conn)
        except Exception as e:
           raise BaadalException(e.message)
        pass

    def createBaadalVM(self, name, image, template, nics, **kwargs):
        """ nics must be None or a list of dictionaries of the format
        {
            net-id : uuid of the network,
            v4-fixed-ip: fixed IPv4 address,
            port-id: uuid of the port if already defined
        }
        """
        # underlying command
        # nova boot --flavor 1 --image 6f0ae131-7190-4230-98e4-8a90285b776a --nic net-id=3893d432-08e9-48b1-975f-e6edae078a1a test07
        # try:
        sec_group = self._network_name_from_id(nics[0]['net-id'])
        server = self.__conn['nova'].servers.create(name, image, template, nics=nics, security_groups=[sec_group], **kwargs)
        return BaadalVM(server=server, conn=self.__conn)
        # except Exception as e:
            # raise BaadalException(e.message)
        # pass

    def createVolume(self, size, imageRef=None, multiattach=False):
        volume = self.__conn['cinder'].volumes.create(size, imageRef=imageRef, multiattach=multiattach)
        return volume

    def createTemplate(self, name, ram, disk, vcpus):
        try:
            flavor = self.__conn['nova'].flavors.create(name, ram, disk)
            return flavor
        except Exception as e:
            raise BaadalException("Could not create flavor" + e)
    
    def getDiskById(self, diskid):
        return self.__conn['cinder'].volumes.get(diskid)

    def images(self, ):
        # return a list of all images
        try:
            imagesList = self.__conn['nova'].images.list()
            # imagesList = [ Image(i) for i in imagesList ]
            return imagesList
        except Exception as e:
            raise BaadalException(e.message)
        pass

    def findImage(self, **kwargs):
        try:
            image = self.__conn['nova'].images.find(**kwargs)
            # return Image(image)
            return image
        except Exception as e:
            raise BaadalException(e.message)
        pass
   
    def hypervisors(self, name=None, id=None):
        try:
            hypervisors = self.__conn['nova'].hypervisors.list()
        except Exception as e:
            raise BaadalException(e.message or _UNKNOWN_ERROR_MSG)

    def templates(self):
        try:
            templates = self.__conn['nova'].flavors.list()
            return templates
        except Exception as e:
            raise BaadalException(e.message)
        pass

    def findTemplate(self, **kwargs):
        try:
            template = self.__conn['nova'].flavors.find(**kwargs)
            return template
        except Exception as e:
            raise BaadalException(e.message)
        pass
    
    def sgroups(self, ):
        try:
            sgroups = self.__conn['neutron'].list_security_groups()
            return sgroups
        except Exception as e:
            raise BaadalException(e.message)

    def networks(self,):
        try:
            networks = self.__conn['nova'].networks.list()
            return networks
        except Exception as e:
            raise BaadalException(e.message)
        pass
    pass

    def _network_name_from_id(self, netid):
        netlist = self.networks()
        for i in netlist:
            if netid == i.id:
                return i.label
            pass
        pass

    def netid_from_name(self, netname):
        for net in self.networks():
            temp = net.to_dict()
        if temp['label'] == netname:
            return temp['id']


class BaadalException(Exception):
    def __init__(self, msg):
        self.msg = msg
        pass
    
    def __str__(self):
        return repr(self.msg)
        pass
    pass
