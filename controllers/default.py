@auth.requires_login()
def home():
    return dict()


def user():
    if request.vars._formname == 'login':
        session.username = request.vars.username
        session.password = request.vars.password
    if request.args(0) == 'not_authorized':
        raise HTTP(403, 'forbidden')
    else:
        if auth.user and request.args(0) in ('login', None):
            redirect('/baadal/user')
        from gluon.html import INPUT, H2, A
        form = auth()
        el = list()
        el.append(H2('Please log in'))
        label = LABEL('Email address')
        label.attributes['_for'] = 'auth_user_username'
        label.add_class('sr-only')
        el.append(label)
        for i in form.elements():
            if isinstance(i, INPUT):
                if i.attributes['_type'] in ('text', 'password'):
                    i.add_class('form-control')
                if i.attributes['_type'] == 'submit':
                    i.add_class('btn btn-primary btn-lg btn-block')
                el.append(i)
        link = A('Request an account', callback='/baadal/user/register')
        link.add_class('btn btn-link')
        el.append(link)
        form.components = el
        form.add_class('form-signin')
        return dict(form=form)


def register():
    return dict()


def register_request():

    return jsonify()
