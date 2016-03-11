from gluon import validators

def userid_in_db(userid):
    validator = validators.IS_IN_DB(db, db.account_requests.userid)
    return validator(userid)[1] == None

def username_is_valid(username):
    return validators.re.match(r'^[A-Za-z][A-Za-z ]{2,}[A-Za-z]$',
                               username) != None

def email_is_valid(email):
    validator = validators.IS_EMAIL(email)
    return validator(email)[1] == None

def email_in_db(email):
    validator = validators.IS_IN_DB(db, db.account_requests.email)
    return validator(email)[1] == None

def userid_is_valid(userid):
    validator = validators.IS_ALPHANUMERIC(userid)
    return validator(userid)[1] == None and len(userid) >= 4
