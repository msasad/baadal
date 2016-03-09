import ConfigParser


config = ConfigParser.ConfigParser()
config.read('/etc/baadal/baadal.conf')


mail_server = config.get('mail', 'server')
mail_sender = config.get('mail', 'sender')
mail_login = config.get('mail', 'login')
mail_support = config.get('mail', 'support')
mailer = BaadalMailer(mail_server, mail_sender, mail_login)
