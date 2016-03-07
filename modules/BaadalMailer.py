from gluon.tools import Mail


class BaadalMailer(object):

    class MailTypes(object):

        class RegistrationSuccessful(object):
            subject = 'Baadal Registration Successful'
            mailbody = "Dear {0[username]},\n\n Your account with username" \
                "{0[loginName]} has been activated.\n\n Welcome to Baadal!"

        class RegistrationDenied(object):
            subject = 'Baadal Registration Denied'
            mailbody = "Dear {0[userName]},\n\nYour registration to Baadal" \
                "has been denied. For any query, send an email to"\
                "{0[supportMail]}"

        class VMRequest(object):
            subject = 'VM request successful'
            mailbody = "Dear {0[username]},\n\nYour VM request has been" \
                " registered successfully and is waiting for approval. You" \
                " will be notified with a separate email after the VM is created."

        class ApprovalReminder(object):
            subject = 'Request waiting for your approval'
            mailbody = "Dear {0[approverName]},\n\n{0[userName]} has made a "\
                "'{0[requestType]}' request on {0[requestTime]}. It is "\
                "waiting for your approval."

        class VMCreated(object):
            subject = 'Your BaadalVM has been created'
            mailbody = "Dear {0[username]},\n\n The VM {0[vm_name]}" \
                " {0[request_time]} is successfully created and is now" \
                " available for use. Following operations are allowed on" \
                " VM:\n 1. Start\n2. Stop\n3. Pause\n4. Resume\n5. Destroy" \
                " \n6. Delete\n\n Default credentials for VM is as follows:" \
                " \nUsername:root/baadalservervm/baadaldesktopvm\n" \
                " Password:baadal\n\n To access VM using assigned private" \
                " IP; SSH to baadal gateway machine using your GCL" \
                " credential .\n username@{0[gateway_server]}\n For other"\
                " details, Please login to Baadal web interface."

        class TaskComplete(object):
            subject = '{0[taskType]} task successful'
            mailbody = "Dear {0[userName]},\n\n The '{0[taskType]}' task for"\
                "VM({0[vmName]}) requested on {0[requestTime]} is complete."

        class VNCAccessActivated(object):
            subject = 'VNC Access to your VM activated'
            mailbody = "Dear {0[userName]},\n\n VNC Access to your VM" \
                "{0[vmName]} was activated on {0[requestTime]}. Details" \
                "follow:\n 1. VNC IP : {0[vncIP]}\n2. VNC Port  :"  \
                "{0[vncPort]}\n\nVNC Access will be active for 30 minutes" \
                "only.\n\n For other details, Please login to baadal WEB" \
                "interface."

        class VMDeleteWarning(object):
            subject = 'Delete Warning to the Shutdown VM'
            mailbody = "Dear {0[userName]},\n\n It has been noticed that your"\
                "VM {0[vmName]} is being shutdown from {0[vmShutdownDate]}."\
                "Kindly use the VM/delete the VM if not required. \n\ If no"\
                "action is taken on the VM, the VM will be automatically"\
                "deleted on {0[vmActionDate]}. \n\n For other details,"\
                "Please login to Baadal web interface."

        class ShutdownBaadal(object):
            subject = 'Baadal Shutdown notice'
            mailbody = "Dear {0[userName]},\n\n Baadal services will be"\
                "shutting down today from 12:00 PM to 6:00 PM for"\
                "maintenance. We will shutdown your VM"\
                "{0[vmName]}({0[vmIp]}) to avoid any corruption of data."\
                "VM will be brought up as soon as possible."

        class VMShutdownWarning(object):
            subject = ''
            mailbody = ''

    mail_footer = "\n\nRegards,\nBaadal Admin\n\n\nNOTE: Please do not "\
        "reply to this email. It corresponds to an unmonitored mailbox. "\
        "If you have any queries, send an email to {0[mail_support]}."

    def __init__(self, mail_server, mail_sender, mail_login=None):
        self.mailer = Mail()
        self.mailer.settings.server = mail_server
        self.mailer.settings.sender = mail_sender
        self.mailer.settings.login = mail_login

    def send(self, mail_type, recipient, context, cc=[]):
        subject = 'Baadal Notification: ' + mail_type.subject
        mailbody = (mail_type.mailbody + self.__class__.mail_footer).\
            format(context)
        return self.mailer.send(to=recipient, subject=subject,
                                message=mailbody)
