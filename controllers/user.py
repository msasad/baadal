#!/usr/bin/python
import logging
logger = logging.getLogger("web2py.app.baadal")
from novaclient.exceptions import NotFound
import MySQLdb as mdb
import ConfigParser
from gluon import *  # @UnusedWildImport
#from gluon import request,session
import json,datetime,time
import threading,os
import Baadal
import paramiko
from utilization import *

if auth.is_logged_in():
   logger.debug("inside controller user.py session is " + str(session))
   logger.debug("inside controller user.py session username is " + str(session.username))
   new_db=mdb.connect("127.0.0.1","root","baadal","baadal")
   n_db=new_db.cursor()
   n_db.execute("select user_id,password from auth_user where username= %s",session.auth.user.username)
   data=n_db.fetchall()
   logger.debug("inside controller user.py data is " + str(data))
   session.username=data[0][0]
   session.password=data[0][1]
   n_db.close()
   new_db.close()

@auth.requires_login()
def index():
    return dict()


@auth.requires_login()
def form():
    logger.info(request.env.REQUEST_METHOD)
    return dict()

def login():
    return dict()

@auth.requires_login()
def my_vms():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                                 session.password)
        images = dict()
        vms = conn.baadal_vms(user=session.auth.user.username)
        response = list()
        for vm in vms:
            vm_properties = vm.properties()
            image_id = vm_properties['image']['id']
            if not images.has_key(image_id):
                try:
                    image = conn.find_image(id=image_id)
                    meta = image.metadata
                    images[image_id] = ' '.join([meta['os_name'],
                        meta['os_version'], meta['os_arch'],
                        meta['os_edition'], meta['disk_size']])
                except NotFound:
                    images[image_id] = 'Image not found'
            vm_properties['image']['info'] = images[image_id]
            response.append(vm_properties)
        #     snapshots = vm.properties()['snapshots']
        #     for index in range(0, len(snapshots)):
        #         snapshots[index]['created'] = convert_timezone(
        #             snapshots[index]['created'])
        #     vm_properties['snapshots'] = snapshots
        return jsonify(data=response)
        #return jsonify(data=vms)
    except Exception as e:
        logger.exception(e.message or str(e.__class__))
        return jsonify(status='fail')
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires_login()
def vm_status():
    try:
        conn = Baadal.Connection(_authurl, _tenant, session.username,
                                 session.password)
        vmid = request.vars.vmid
        vm = conn.find_baadal_vm(id=vmid)
        if vm:
            return jsonify(vm_status=vm.get_status())
    except Exception as e:
        logger.exception(e.message() or str(e.__class__))
    finally:
        try:
            conn.close()
        except NameError:
            pass


@auth.requires_login()
def requests():
    try:
        if request.vars.action == 'patch':
            logger.info('patching request')
            db(db.vm_requests.id == request.vars.id).update(
                extra_storage=request.vars.storage,
                public_ip_required=1 if request.vars.public_ip == 'yes' else 0,
                flavor=request.vars.flavor)
            db.commit()
            return jsonify();
        elif request.vars.action == 'delete':
            db(db.vm_requests.id == request.vars.id).delete()
            return jsonify(action='delete')
    except Exception as e:
        logger.exception(e)
        return jsonify(status='fail', message=e.message or str(e.__class__))



@auth.requires_login()
def my_requests():
    rows = db((db.vm_requests.requester == session.auth.user.username) & (db.vm_requests.state < 2)).select()
    l = rows.as_list()
    net_names = dict()
    STATES = ['Pending', 'Pending Admin Approval', 'Approved']
    for i in l:
        # i['flavor'] = flavor_info(i['flavor'])
        net_id = i['sec_domain']
        if not net_names.has_key(net_id):
            net_names[net_id] = network_name_from_id(net_id)
        i['sec_domain'] = net_names[net_id]
        i['request_time'] = str(datetime.datetime.fromtimestamp(i['request_time']))
        i['public_ip_required'] = 'Required' if i['public_ip_required'] == 1 \
            else 'Not Required'
        i['state'] = STATES[i['state']]
    return jsonify(data=l)


@auth.requires_login()
def my_requests_list():
    return dict()


def register():
    return dict()


###################################GRAPH##############################


#convert graph type from client side into ceilometer type
def get_graph_type(g_type):
    if g_type=="cpu":
        return "cpu_util"
    if g_type=="ram":
        return "memory.usage"
    if g_type=="disk":
        output=[]
        output.append("disk.write.bytes.rate")
        output.append("disk.read.bytes.rate")
        logger.debug(output)
        return output
    if g_type=="nw":
        output=[]
        output.append("network.incoming.bytes.rate")
        output.append("network.outgoing.bytes.rate")
        logger.debug(output)
        return output
    

def get_limit_value(graph_period):
    if graph_period == 'hour':	
        value=12
    elif graph_period == 'day':
        value=12*24
    elif graph_period == 'month':
        value=12*24*30
    elif graph_period == 'week':
        value=12*24*7
    elif graph_period == 'year':
        value=12*24*30*12
    
    return value

  
#fetching graph data from ceilometer 
def fetch_graph_data(vm_info):
    result=[]
    try:

        for data in vm_info:
            info={}
            for key,value in data.__dict__.items():
                if key=='volume':
                    info['y']=value
                if key=='timestamp':
                    str_date=str(value[0:18]).split("T")
                    datetime=str_date[0] + " " + str_date[1]
                    info['x']=int(time.mktime(time.strptime(datetime, "%Y-%m-%d %H:%M:%S")))*1000
            result.append(info)

        return result
    except Exception as e:
        logger.exception(e.message() or str(e.__class__))


@auth.requires_login()
def create_graph():
    ret={}
    vmid=request.vars['vmIdentity']
    graph_period=request.vars['graphPeriod']
    vm_ram=request.vars['vm_RAM']
    g_type=request.vars['graphType']
    m_type=request.vars['mtype']
    result=[]
    logger.debug(vmid)
    logger.error(graph_period)
    logger.error(vm_ram)  
    logger.error(g_type)
    gtype=get_graph_type(g_type)
    logger.error(gtype)
    logger.error("welcome")
    limit=get_limit_value(graph_period)
    logger.debug(limit)
    try:
        logger.debug(len(vmid))
        if (len(vmid)==0):
            ret['data']=[]
            json_str = json.dumps(ret,ensure_ascii=False)
            return json_str
        conn = Baadal.Connection(_authurl, _tenant, session.username,session.password)
        if (g_type=="ram") or (g_type=="cpu"):
            vm_info = conn.fetch_sample_data(vmid,gtype,limit)
           
            graph_data=fetch_graph_data(vm_info)
            
            result=graph_data
           
        if g_type=="disk":
            for graph_type in gtype:
                vm_info = conn.fetch_sample_data(vmid,graph_type,limit)
                graph_data=[]
                graph_data=fetch_graph_data(vm_info)
                result.append(graph_data)
        if g_type=="nw":
                vmidtext= str(vmid)+"-t"
                logger.debug(vmidtext)
                command ="source admin-openrc.sh && " + "ceilometer resource-list| grep " + vmidtext + "| cut -f 2 -d \" \""
                logger.debug(command)
                vmid = execute_remote_cmd("127.0.0.1", "root", command, password = "baadal")
                vmid = vmid.rstrip('\n')
                logger.debug(vmid)
                
                for graph_type in gtype:
                    logger.debug(graph_type)
                    vm_info = conn.fetch_sample_data(vmid,graph_type,limit)
                    logger.debug(vm_info)
                    graph_data=[]
                    graph_data=fetch_graph_data(vm_info)
                    result.append(graph_data)
        title=check_graph_type(g_type,vm_ram,m_type)
        host_cpu=request.vars['host_CPU']
        ret['valueformat']=check_graph_period(graph_period)
        ret['y_title']=title['y_title']
        ret['g_title']=title['g_title']
        mem=float(vm_ram)/(1024) if int(vm_ram)>1024 else vm_ram
        ret['data']=result
        ret['mem']=mem
        if g_type=='disk':
            ret['legend_read']='disk read'
            ret['legend_write']='disk write'
        elif g_type=='nw':
            ret['legend_read']='network incoming'
            ret['legend_write']='network outgoing'
        elif g_type=='cpu':
            ret['name']='cpu'
        else:
            ret['name']='mem'
        json_str = json.dumps(ret,ensure_ascii=False)
	logger.error(json_str)
        return json_str
    except Exception as e:
        logger.exception(e.message() or str(e.__class__))


@auth.requires_login()
def show_vm_performance():
    try:
        logger.exception("Entered Performance!!!!!!!!!!!!!")
        logger.exception(session.username)
	logger.exception(session.password)
	logger.exception(_authurl)
	logger.exception(_tenant)
        vmid=request.vars['vmid']
	logger.error(vmid)
        conn = Baadal.Connection(_authurl, _tenant, session.username,session.password)
        logger.exception(conn)
        vm_info = conn.fetch_sample_data(str(vmid),"cpu_util",1)
	logger.exception(vm_info)
        if (vm_info == None or len(vm_info)==0):
                 return dict(m_type="vm",vm_ram="",vm_cpu="",vm_identity="",vm_id = "")
        logger.debug("mirror") 
        for data in vm_info:
            logger.exception("inside for loop")
            info={}
	    logger.debug(data)
            for key,value in data.__dict__.items():
                if key=='metadata':
                    logger.debug(value)
                    ram=value['flavor.ram']
                    cpu=value['vcpus']
                logger.debug("mini baadal")
        return dict(m_type="vm",vm_ram=ram,vm_cpu=cpu,vm_identity=vmid,vm_id = vmid)
    except Exception as e:
        logger.exception(e.message() or str(e.__class__))
    
    finally:
        try:
            conn.close()
        except NameError:
            pass

def vpn():
   return dict()

def vpn_setup_guide():
   return dict()

@auth.requires_login()
def request_user_vpn():
    var = request_vpn()
    logger.debug("request user vpn var value "+str(var))
    #if var== 1 :
        #session.flash = T("Download your client.conf ca.crt baadalVPN.crt  baadalVPN.key files from the link given below  ")

    #elif var == 2 :
        #session.flash =T("Unable to process  your Request. Please contact Baadal Team")
    #else :
        #session.flash = "You already have VPN files  you can  download it from  Download option "
    redirect(URL(r = request, c = 'user', f = 'vpn'))


def download_vpn_keys():
    user_info=get_vpn_user_details()
    logger.debug(type(user_info))
    user_name=user_info['username']
    logger.debug(user_name+"\n")
    file_name = user_name+'_baadalVPN.tar'
    file_path = '/home/www-data/web2py/application/baadal/private/VPN/' + str(file_name)
    logger.debug(file_path+"\n")

    #import contenttype as c
    response.headers['Content-Type'] = "application/zip"
    #response.headers['ContentType'] ="application/octet-stream";
    response.headers['Content-Disposition']="attachment; filename=" +file_name
    logger.debug("******************************************************")
    try:
        return response.stream(get_file_stream(file_path),chunk_size=4096)
    except Exception:
        #session.flash = "Unable to download your VPN files. Please Register first if you have not registered yet."
        logger.debug("Unable to download your VPN files. Please Register first if you have not registered yet.")

    redirect(URL(r = request, c = 'user', f = 'vpn'))


def execute_remote_cmd(machine_ip, user_name, command, password = None, ret_list = False):

    logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))
    output = None
    if machine_ip=="localhost":
        output=os.popen(command).readline()
        logger.debug(output)
    else:
        try:
            #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            logger.debug("----------------->>> ssh")
            ssh = paramiko.SSHClient()
            logger.debug("----------------->>> ssh")
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(machine_ip, username = user_name, password = password)
            logger.debug("Connected to host %s " % machine_ip)
            stdin,stdout,stderr = ssh.exec_command(command)  # @UnusedVariable
    
            output = stdout.readlines() if ret_list else "".join(stdout.readlines())

            error = "".join(stderr.readlines())
            if (stdout.channel.recv_exit_status()) != 0:
                raise Exception("Exception while executing remote command %s on %s: %s" %(command, machine_ip, error))
        except paramiko.SSHException:
            log_exception()
            raise
        finally:
            if ssh:
                ssh.close()

    return output

