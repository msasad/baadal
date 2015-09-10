def index():
    form = FORM(INPUT(_name='vmid', _id='vmid'),
            INPUT(_class='task-button',_type='button', _id='start', _name='start', _value='start'),
            INPUT(_class='task-button',_type='button', _name='pause', _value='pause'),
            INPUT(_class='task-button',_type='button', _name='shutdown', _value='shutdown'),
            INPUT(_class='task-button',_type='button', _name='resume', _value='resume'),
            )
    script = """
    <script>
    (function(){
            var $buttons = $('.task-button');
            $buttons.each(function(){
              var $this = $(this);
              $this.on('click', function(){
                $.ajax({
                    type : 'POST',
                    url : 'baadal/action/'+ this.name + '.json',
                    data : {
                        vmid : $('#vmid').val()
                    },
                    success : function (response) {
                        console.log(response);
                    }
                });
              });
              console.log(this.name);
            });
        })();
        </script>
        """
    response.script = script
    return dict(form=form)
def home():
    return dict()