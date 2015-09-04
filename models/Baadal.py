#!/usr/bin/python
import test
import logging
from keystoneclient.auth.identity import v2
from keystoneclient import session
import os
import datetime

class Machine:
    def __init__(self, ):
        self.hostname = ""
        self.config = {
                memory : None,
                storage : None,
                extra_storage : None,
                cpu : None,
                private_ip : None,
                public_ip : None
        }
        
class BaadalVM:
    def  __init__(self, id=None, server=None, conn=None):
        if id != None and server != None:
            raise BaadalException('Cannot initialise server, please specify either server or id')
        else:
            import novaclient.v2.servers
            if isinstance(server, novaclient.v2.servers.Server):
                self.server = server
                self.__conn = conn

        #create an object corresponding to an existing VM with specified ID
        #usedb
        self.name = self.server.name
        self.id = None
        self.identity = None
        self.hostid = None
        self.vnc_port = None
        self.purpose = None
        self.datastore = None
        self.template_id = None
        self.expiry_date = None
        self.start_time = None
        self.security_domain = None
        self.snapshots = []
        #self.server = novaclient.v2.servers.Server
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
            #debug.log(e)
            raise BaadalException(e)
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
            #debug.log(e)
            raise BaadalException(e)
        pass
        
    def reboot(self, soft=True):
        """
        reboot the Virtual Machine
        params:
            soft: bool, True for soft reboot, False for hard reboot, default True
        return: None
        """
        try:
            if soft == True:
                res = self.server.reboot(reboot_type='REBOOT_SOFT')
            else:
                res = self.server.reboot(reboot_type='REBOOT_HARD')
        except Exception as e:
            #debug.log(e)
            raise BaadalException(e)

    def delete(self, ):
        try:
            res = self.server.delete()
        except Exception as e:
            #debug.log(e)
            raise BaadalException(e)
        pass

    def createSnapshot(self,snapshot_name=None):
        try:
            snapshot_name = snapshot_name or self.server.name + "snapshot" + datetime.datetime.now().isoformat()
            snapshot_id = self.server.create_image(snapshot_name)
            snapshot_image = self.__conn['nova'].findImage()
            return snapshot_id
            #return Snapshot(snapshot, self.server)
        except Exception as e:
            #debug.log(e)
            raise BaadalException(e)
        pass

    def refreshStatus(self):
        #refresh connection to a modified VM
        self.server = self.server.manager.find(id=self.server.id)

    def migrate(self, target_host, live=False):
        try:
            if live == True:
                res = self.server.migrate(dest)
            else:
                res = self.live_migrate(dest)
        except Exception as e:
            #debug.log(e)
            raise BaadalException(e)
        pass

    def revertSpanshot(self, snapshot_id):
        #usedb
        pass

    def getXml(self, ):
        return self.server.to_dict()
        pass

    def __getattr__(self, attr):
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

    def getStatus(self, ):
        STATUS = {
                'ACTIVE' : 'Running',
                'SHUTOFF' : 'Shutdown',
                }
        self.refreshStatus()
        return STATUS[self.server.status]
        pass

    def clone(self, clone_name=None):
        """
        create clone of the selected Virtual Machine
        params:
            clone_name: name of the new clone VM to be created (optional),
            an automatically generated name is used if clone_name is not
            supplied
        return:
        """

        #create a snapshot of the  machine
        #create a new vm using the newly created snapshot
        #delete the snapshot
        try:
            snapshot_id = self.server.create_image("temp")
            clone_name = clone_name or self.server.name + '_clone'
            flavor_id = self.server.flavor['id']
            image = self.__conn['nova'].images.find(id=snapshot_id)
            while image.status != 'ACTIVE':
                image = self.__conn['nova'].images.find(id=snapshot_id)
                pass
            else:
                clone = self.server.manager.create(clone_name, image,
                    self.__conn['nova'].flavors.find(id=flavor_id))
                while clone.status != 'ACTIVE':
                    clone = clone.manager.find(id=clone.id)
                else:
                    image.delete()
                    attached_disks = self.attachedDisks()
                    for i in attached_disks:
                        self.__conn['cinder'].volumes.create_server_volume(clone.id, i['id'], i['path'])
            return clone
        except  Exception as e:
        #debug.log(e)
            raise BaadalException(e)
        pass
    
    def attachedDisks(self,):
        volume_ids = self.server.__getattr__('os-extended-volumes:volumes_attached')
        disk_list = []
        for i in volume_ids:
            volume = self.__conn['cinder'].volumes.find(id=i['id'])
            attachments_list = volume.attachments
            for entry in attachments_list:
                if entry['server_id'] == self.server.id:
                    devicepath = entry['device']
                    disk_list.append({
                        'id' : i['id'],
                        'path' : devicepath
                        })
                    pass
            pass
        return disk_list
            
    def lastSnapshot(self, ):
        #get the last snapshot of the current VM or return None if no snapshots found
        #usedb
        pass

    def attachDisk(self, disk, device_path):
        """
        attach a disk to a Virtual Machine
        params:
            disk: instance of disk to be attached
            device_path: path in the system where the disk is to be attached
        return: 
        """

        try:
            self.__conn['cinder'].volumes.create_server_volume(self.server.id, disk.id, device_path)
        except Exception as e:
            #debug.log(e)
            raise BaadalException(e)
        pass

    def update(self, **kwargs):
        #update metadata/config
        pass
    
    pass

class Image:
    def __init__(self, image):
        self.__image = image
        self.type = None
        pass
    
    def delete(self):
        pass
    
    pass

class Disk:
    def __init__(self, ):
        pass
        
    def attachTo(self, vm, device_path):
        try:
            self.__conn['cinder'].volumes.create_server_volume(vm.id, self.id, device_path)
        except Exception as e:
            #debug.log(e)
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
            os : None,
            name : None,
            type : None,
            edition : None
        } 
        self.arch = None
        self.hdd = None
        self.type = None
        self.tag = None
        self.datastore = None
        self.owner = None
        self.is_active = None

class Host(Machine):
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
        from cinderclient import client as cclient 
        auth = v2.Password(auth_url=authurl, username=username,
                password=password, tenant_name=tenant_name)
        sess = session.Session(auth=auth)
        self.__conn = {}
        self.__conn['nova'] = client.Client('2', session=sess)
        self.__conn['cinder'] = cclient.Client('2', session=sess)
        #self.__cinder = cclient.Client("2", session=sess)
        #self.__conn = client.Client("2", session=sess)
        pass

    def close(self, ):
        pass

    def usage(self, attribute_list=None):
        USAGE_PARAMS = {
                'free_storage' : 'free_disk_gb',
                'used_storage' : 'local_gb_used',
                'total_storage' : 'local_gb',
                'free_memory' : 'free_ram_mb',
                'used_memory' : 'memory_mb_used',
                'total_memory' : 'memory_mb',
                'total_vms' : 'running_vms',
                'load_avg' : 'current_workload',
                'vcpus' : 'vcpus',
                'vcpus_used' : 'vcpus_used'
                }
        values = {}
        stats = self.__conn['nova'].hypervisor_stats.statistics().to_dict()
        attribute_list = attribute_list or USAGE_PARAMS.keys()
        for item in attribute_list:
            values[item] = stats[USAGE_PARAMS[item]]
        return values
        pass

    def baadalVMs(self, ):
        #return a list of VMs running on the host
        try:
            serverList = self.__conn['nova'].servers.list()
            serverList = [ BaadalVM(server=i, conn=self.__conn) for i in serverList ]
            return serverList
        except Exception as e:
            raise BaadalException(e)
        
        #wrap each object of the list of novaclient.v2.servers.Server objects into
        #a list of BaadalVM objects and return it
        pass

    def findBaadalVM(self, **kwargs):
        try:
            baadalVM = self.__conn['nova'].servers.find(**kwargs)
            return BaadalVM(server=baadalVM, conn=self.__conn)
        except NotFound:
            raise BaadalException("No matching VM found")
        pass

    def createBaadalVM(self, name, image, template, **kwargs):
        server = self.__conn['nova'].servers.create(name, image, template, **kwargs)
        return BaadalVM(server=server, conn=self.__conn)
        pass

    def createTemplate(self, name, ram, disk, vcpus):
        try:
            flavor = self.__conn['nova'].flavors.create(name, ram, disk)
        except:
            raise BaadalException("Could not create flavor")
    
    def images(self, ):
        #return a list of all images
        try:
            imagesList = self.__conn['nova'].images.list()
            #imagesList = [ Image(i) for i in imagesList ]
            return imagesList
        except Exception as e:
            raise BaadalException(e)
        pass

    def findImage(self, **kwargs):
        try:
            image = self.__conn['nova'].images.find(**kwargs)
            #return Image(image)
            return image
        except Exception as e:
            raise BaadalException(e)
        pass
    
    def templates(self):
        try:
            templates = self.__conn['nova'].flavors.list()
            return templates
        except Exception as e:
            raise BaadalException(e)
        pass

    def findTemplate(self, **kwargs):
        try:
            template = self.__conn['nova'].flavors.find(**kwargs)
            return template
        except Exception as e:
            raise BaadalException(e)
        pass

    pass

class BaadalException(Exception):
    def __init__(self, msg):
        self.msg = msg
        pass
    
    def __str__(self):
        return repr(self.msg)
        pass
    pass
