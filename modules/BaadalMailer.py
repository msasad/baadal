from gluon.tools import Mail

class BaadalMailer(object):
    class MailTypes(object):
        class RegistrationSuccessful(object):
            subject = 'Baadal Registration Successful'
            mailbody = """Dear {0[userName]},\n\n Your account
                with username {0[loginName]} has been activated.\n\n Welcome to
                Baadal!"""

        class RegistrationDenied(object):
            subject = ''
            mailbody = ''

        class VMRequest(object):
            subject = ''
            mailbody = ''

        class ApprovalReminder(object):
            subject = ''
            mailbody = ''

        class VMCreated(object):
            subject = ''
            mailbody = ''

        class TaskComplete(object):
            subject = ''
            mailbody = ''

        class VNCAccessActivated(object):
            subject = ''
            mailbody = ''

        class VMDeleteWarning(object):
            subject = ''
            mailbody = ''

        class ShutdownBaadal(object):
            subject = ''
            mailbody = ''

        class VMShutdownWarning(object):
            subject = ''
            mailbody = ''

        class RegistrationSuccessful(object):
            subject = ''
            mailbody = ''

    class SUBJECT(object):
        REGISTRATION_SUCCESSFUL = 'Baadal Registration Successful'
        REGISTRATION_DENIED = "Baadal Registration Denied"
        VM_REQUEST = "VM request successful"
        APPROVAL_REMINDER = "Request waiting for your approval"
        VM_CREATION = "VM created successfully"
        TASK_COMPLETE = "{0[taskType]} task successful"
        VNC_ACCESS = "VNC Access to your VM activated"
        DELETE_WARNING = "Delete Warning to the Shutdown VM" 
        SHUTDOWN_WARNING = "Shutdown Warning to the unused VM"
        BAADAL_SHUTDOWN = "VM Shutdown notice"

    class MAILBODY(object):
        REGISTRATION_SUCCESSFUL = """Dear {0[userName]},\n\n Your account
            with username {0[loginName]} has been activated.\n\n Welcome to
            Baadal!"""
        REGISTRATION_DENIED = """Dear {0[userName]},\n\n Your
            registration to Baadal has been denied. For any query, send an
            email to {0[supportMail]}"""
        VM_REQUEST = """Dear {0[userName]},\n\n Your request for
            VM({0[vmName]}) creation has been successfully registered.
            Please note that you will be getting a separate email on
            successful VM creation."""
        APPROVAL_REMINDER = """Dear {0[approverName]},\n\n{0[userName]}
            has made a '{0[requestType]}' request on {0[requestTime]}. It is
            waiting for your approval."""

        
    def __init__(self,):
        global mail_server, mail_sender, mail_username, mail_password
        self.mailer = gluon.tools.Mail()
        self.mailer.settings.sender = mail_sender
        self.mailer.settings.login = '%s:%s' % (mail_username, mail_password)
        pass
    
    def send(mail_type, recipient, cc=[],):
        assert mail_type in [ i for i in dir(BaadalMailer.MailTypes) if not \
                i.startswith('__') ]
        subject = mail_type.subject
        mailbody = mail_type.mailbody

        self.mailer.send(recipient.username

        subject = getattr(BaadalMailer.SUBJECT, mail_type)
        mailbody = getattr(BaadalMailer.MAILBODY, mail_type)

    def  
