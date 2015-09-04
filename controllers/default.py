def index():
    form = FORM(INPUT(_name='vmid', _id='vmid'),
            INPUT(_class='task-button',_type='button', _id='start', _name='start', _value='start'),
            INPUT(_class='task-button',_type='button', _name='pause', _value='pause'),
            INPUT(_class='task-button',_type='button', _name='shutdown', _value='shutdown'),
            INPUT(_class='task-button',_type='button', _name='resume', _value='resume'),
            )
    return dict(form=form)
