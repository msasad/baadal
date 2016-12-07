import paramiko,os
import logging
import logging.config
logger = logging.getLogger("web2py.app.baadal")

def execute_remote_cmd_on_port(machine_ip, user_name, command, port_no ,ret_list = False, password = None):

    logger.debug("executing remote command %s on %s with %s on %s port no:"  %(command, machine_ip, user_name,port_no))
    output = None
    if machine_ip=="localhost":
        output=os.popen(command).readline()
        logger.debug(output)
    else:
        logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))

        try:
            logger.debug("Inside try")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(machine_ip,port_no,username = user_name, password = password)
            logger.debug("Connected to host %s " % machine_ip)
            stdin,stdout,stderr = ssh.exec_command(command)  # @UnusedVariable

            output = stdout.readlines() if ret_list else "".join(stdout.readlines())
            #logger.debug("Output : %s " % output)

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

def execute_remote_cmd(machine_ip, user_name, command, password = None, ret_list = False):

    logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))
    output = None
    if machine_ip=="localhost":
        output=os.popen(command).readline()
        logger.debug(output)
    else:
        try:
            ssh = paramiko.SSHClient()
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


def get_vpn_user_details():
   logger.debug("inside get_vpn_user_details")
   user_info=db((db.auth_user.id==auth.user.id)).select(db.auth_user.ALL)
   logger.debug("userinfo"+ str(user_info))
   for info in user_info:
       user_details={'username':info['username'],
         'first_name':info['first_name'],
          'last_name':info['last_name']}
       return user_details


#def transfer_vpn_files(user_name,vpn_ip,passwd=None):
def transfer_vpn_files(user_name,vpn_ip,password=None):
    logger.debug("inside transfer_vpn_files")
    import paramiko
    logger.debug("Inside transfer vpn files")
    paramiko.util.log_to_file('/tmp/paramiko.log')
    logger.debug("executing remote ftp on %s with %s:"  %(vpn_ip, user_name))
# Open a transport
    port = 22
    transport = paramiko.Transport((vpn_ip, port))
    logger.debug("transport :  " + str(transport))
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    logger.debug("privatekeyfile : " + str(privatekeyfile))
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    logger.debug("my key var is satisfied : " + str(mykey))
# Auth
    logger.debug("before connect transport")
    transport.connect(username ='root',pkey = mykey)
    logger.debug("after connect transport")
# Go!
    sftp = paramiko.SFTPClient.from_transport(transport)
# Download
    logger.debug("user _name"+str(user_name))
    filepath="/etc/openvpn/easy-rsa/keys/tar_files/"+str(user_name)+"_baadalVPN.tar"
    localpath="/home/www-data/web2py/applications/baadal/private/VPN/"+str(user_name)+"_baadalVPN.tar" 
    logger.debug("local path is "+str(user_name))

    var=sftp.get(filepath,localpath)

# Close
    sftp.close()
    transport.close()

def request_vpn():
    logger.debug("inside request vpn function")
    user_info=get_vpn_user_details()
    logger.debug(type(user_info))
    user_name=user_info['username']
    cmd="./vpn_client_creation.sh "+ str(user_name)
    vpn_ip="10.237.22.29"
    #vpn_ip=config.get("VPN_CONF","vpn_server_ip")
    passwd="baadal"
    #password=config.get("VPN_CONF","passwd")

    try:
        logger.debug("vpn ip value is :"+str(vpn_ip))
        #var = execute_remote_cmd_on_port(vpn_ip, 'root', cmd, 22 ,True, password = None)
        #var = execute_remote_cmd(vpn_ip, 'root',cmd, passwd, True)
        #logger.debug("var value"+str(var))
        logger.debug("return back to request_vpn")
        transfer_vpn_files(user_name,vpn_ip,passwd)
        logger.debug("var value in  VPN :"+str(var))
        if  "false" in str(var):
            return 1
        elif "true" in str(var):
            return 3
        #transfer_vpn_files(user_name,vpn_ip,passwd)
    except Exception:
        return 2


