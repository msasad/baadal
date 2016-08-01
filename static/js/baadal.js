/*global

console,
Handlebars,
jQuery
*/

var baadalApp = (function ($) {
  'use strict';
  baadalApp = {};

  baadalApp.requestAction = function (data) {
    return $.ajax({
      url: '/baadal/action/index.json',
      type: 'post',
      data: data
    });
  };

  baadalApp.serialize = function (temp) {
    var obj = {}, i, curr;
    for (i = temp.length - 1; i >= 0; i -= 1) {
      curr = temp[i];
      obj[curr.name] = curr.value;
    }
    return obj;
  };

  baadalApp.generateTicketLink = function (error) {
    var ticket_id = error.split(' ')[1],
      url = document.location.origin + '/admin/default/ticket/' + ticket_id;
    console.log(url);
  };

  baadalApp.ipArrayToString = function (ipArray, usebr) {
    if (!Array.isArray(ipArray)) {
      return ipArray;
    }
    var arr = [], i, str, keys, j;
    ipArray.forEach(function (ip, index, full) {
      str = '';
      keys = Object.keys(ip);
      keys.forEach(function (el) {
        str += el + ':' + full[index][el] + ' ';
      });
      arr.push(str);
    });
    return arr.join(usebr ? '<br>' : '\n');
  };

  baadalApp.ipObjectToString = function (object) {
    var strings = [], i, ips, ip;
    Object.keys(object).forEach(function (network) {
      object[network].forEach(function (ip) {
        strings.push('MAC: ' + ip['OS-EXT-IPS-MAC:mac_addr'] + ' IP: ' + ip.addr);
      });
    });
    return strings.join('<br/>');
  };

  baadalApp.filterArrayObject = function (object, array_name, field_name, value) {
    if (object.hasOwnProperty(array_name)) {
      var array = object[array_name], newarray = [];
      array.forEach(function (elem) {
        if (elem[field_name] === value) {
          newarray.push(elem);
        }
      });
      object[array_name] = newarray;
      return object;
    }
  };

  baadalApp.populateSnapshots = function (data, template) {
    template = Handlebars.compile(template);
    return template(data);
  };

  baadalApp.getSettingsButtonsMarkup = function (status, template) {
    var actions = {
      'ACTIVE': 'shutdown',
      'SHUTOFF': 'start',
      'ERROR': 'start'
    },
      glyphicons = {
        'ACTIVE': 'stop',
        'SHUTOFF': 'play',
        'ERROR': 'play'
      };
    return template.replace(/\{\{action\}\}/g, actions[status]).
        replace(/\{\{icon\}\}/g, glyphicons[status]);
  };

  baadalApp.vmView = {
    init: function (config) {
      this.table = $('#' + config.tableid);
      this.modalid = config.modalid;
      this.templateURL = config.templateURL;
      this.dataURL = config.dataURL;
      this.setupTable(config.isAdmin);
      this.attachEvents();

      var promise1,
        promise2,
        $this = this;
      promise1 = $.ajax({
        url: $this.templateURL,
        headers: {
          role: config.isAdmin ? 'admin' : 'user'
        }
      });
      promise1.then(function (response) {
        $this.dialogTmpl = Handlebars.compile(response);
      });
    },

    setupTable: function (isAdmin) {
      var dataURL = this.dataURL,
        emptyMsg = "You don't have any VMs currently! You may request" +
              " one <a href=\"./form\">here</a>",
        columns,
        $dt;
      columns = isAdmin ? [
        { "data": "name" },
        { "data": "status" },
        { "data": "owner" },
        { "data": "flavor.id" },
        { "data": "image.info" },
        { "data": null },
        { "data": "OS-EXT-SRV-ATTR:instance_name"  },
        { "data": "OS-EXT-SRV-ATTR:host" },
        { "data": null }
      ] : [
        { "data": "name" },
        { "data": "status" },
        { "data": "owner" },
        { "data": "flavor.id" },
        { "data": "image.info" },
        { "data": null },
        { "data": null }
      ];

      this.$dt = this.table.DataTable({
        "responsive": true,
        "ajax": {
          "url": dataURL,
          "error": function (response, code) {
            var error = response.getResponseHeader('web2py_error');
            if (error) {
              baadalApp.generateTicketLink(error);
            } else if (response.status === 401) {
              document.location.reload();
            }
          }
        },
        "oLanguage": {
          "sEmptyTable": emptyMsg
        },
        "aoColumnDefs": [{
          "aTargets": [5],
          "bSortable": false,
          "mData": null,
          "mRender": function (data, type, full) {
            if (type === 'display' || type === 'filter') {
              var addresses = data.addresses;
              if (typeof addresses === "object") {
                return baadalApp.ipObjectToString(addresses);
              }
            }
            return data;
          }
        }, {
          "aTargets": [isAdmin ? 8 : 6],
          "bSortable": false,
          "mData": null,
          "mRender": function (data, type, full) {
            if (type === 'display') {
              return baadalApp.getSettingsButtonsMarkup(data.status,
                      document.getElementById('btns-tmpl').innerHTML);
            }
            return data;
          }
        }],
        "columns": columns,
        "fnCreatedRow": function (nRow, aData, iDataIndex) {
          nRow.setAttribute('data-vmid', aData.id);
        }
      }); // end dataTables initialization

      $dt = this.$dt;
      $(document).on('init.dt', function () {
        setInterval($dt.ajax.reload, 30 * 1000);
      });
    }, // setupTable

    attachEvents: function () {
      var $this = this,
        actionbtn = '#' + $this.modalid + ' .btn-action',
        btn_vm_del_yes = '#vm-delete-confirmation button[name=btn-yes]',
        btn_vm_del_no = '#vm-delete-confirmation button[name=btn-no]',
        action,
        action_confirmed = false,
        data = {},
        promise;

      $(document.body).on('click', '#btn-disk-request', function (e) {
        e.preventDefault();
        data.disksize = document.getElementById('disksize').value;
        promise = baadalApp.requestAction(data);
        promise.then(function (response) {
          console.log(response);
          if (response.message) {
            $('#modal-info-message').html(response.message).fadeIn().siblings().hide();
          }
        });
      });

      // Event handler for click of open-console button
      $this.table.on('click', '.btn-console', function (e) {
        var vmid = $(this).closest('tr').data('vmid');
        $.ajax({
          url: '/baadal/action/index.json',
          data: {
            vmid: vmid,
            action: 'get-console-url',
            urlonly: true
          },
          success: function(response) {
            window.open(response.message);
          }
        });
      });

      // Event handler for click of settings button
      $this.table.on('click', '.btn-settings', function (e) {
        var tr = this.closest('tr'),
          context = $this.$dt.row(tr).data(),
          html, keys;
        context['ip-addresses'] = baadalApp.ipObjectToString(context.addresses, true);
        keys = Object.keys(context.addresses);
        console.log(context.addresses);
        html = $this.dialogTmpl(context);
        $(document.body).prepend(html);
        $this.$modal = $('#' + $this.modalid).modal('show');
        if (context.addresses[keys[0]].length === 2) {
            $this.$modal.find('[data-action=attach-public-ip]').attr('disabled', 'disabled');
        }
        $this.$modal.on('hidden.bs.modal', function () {
          $this.$modal.remove();
          $this.$dt.ajax.reload();
        });
        $this.$modal.footer = $this.$modal.find('.panel-footer');
      });

      $(document.body).on('click', btn_vm_del_no, function () {
        $('#vm-delete-confirmation').fadeOut();
      });

      $(document.body).on('click', '#update-collaborators', function (e) {
        e.preventDefault();
        data.action = 'update-collaborators';
        data.collaborators = $('#collaborators').val();
        $.ajax({
            type: 'post',
            url: '/baadal/action/index.json',
            data: data,
            success: function(response) {
                console.log(response);
                $('#modal-info-message').html(response.message).fadeIn().siblings().hide();
            },
            error: function(error, response, code) {
              $('#modal-error-message').html(error.responseText).fadeIn().siblings().hide();
              console.log(error, response, code);
            }
        });
      });
      $(document.body).on('click', btn_vm_del_yes, function () {
          data.action = 'delete';
          $.ajax({
              type: 'post',
              url: '/baadal/action/index.json',
              data: data,
              success: function(response) {
                  console.log(response);
                  $('#modal-info-message').html(response.message).fadeIn().siblings().hide();
              },
              error: function(error, response, code) {
                  console.log(error, response, code);
              }
          });
      });

      $(document.body).on('click', '#btn-resize-request', function (e) {
        e.preventDefault();
        data.vmid = $('#vmid').val();
        data.new_flavor = $('#new_flavor').val();
        data.name = $('#vmid').data().vmname
        promise = $.ajax({
          type: 'post',
          url: '/baadal/post_request/request_resize.json',
          data: data
        });
        promise.then(function (response) {
          console.log(response);
          if (response.status === 'success') {
            $('#modal-info-message').html('Resize request has been successfully posted.').fadeIn().siblings().hide();
          }
        });
      });

      // Event handler for click of action buttons on settings dialog
      $(document.body).on('click', actionbtn, function () {
        promise = undefined;
        var vmid = $(this).parent().data('vmid'),
          html,
          span,
          flavor_selector,
          promise2;
        action = $(this).data('action');
        data.action = action;
        data.vmid = vmid;
        switch (action) {
        case 'delete':
           $('#vm-delete-confirmation').fadeIn().siblings().hide();
        //   $this.children.namedItem('btn-yes').addEventListener('click', function () {
        //     action_confirmed = true;
        //   });
           break;
        case 'add-virtual-disk':
          $('#disk-size-input').fadeIn().siblings().hide();
          break;
        case 'resize':
          promise2 = $.getJSON('/baadal/ajax/configs.json');
          flavor_selector = document.getElementById('new_flavor');
          promise2.then(function (response) {
            response.forEach(function (flavor, index) {
              flavor_selector.options.add(new Option(flavor.vcpus + 'CPU, ' +
                flavor.ram + 'MB RAM', flavor.id));
            });
            $('#resize-form').fadeIn().siblings().hide();
          });
          break;
        case 'manage-users':
          $('#edit-collaborators').fadeIn().siblings().hide();
          break;
        default:
          promise = baadalApp.requestAction(data);
        }
        if (promise) {
          promise.then(function (response) {
            console.log(response);
            if (response.message) {
              $('#modal-info-message').html(response.message).fadeIn().siblings().hide();
            }
          });
        }
      });

      // Event handler for snapshot-restore buttons
      $(document.body).on('click', '#' + $this.modalid + ' .snapshot-restore', function (e) {
        var vmid = document.getElementById('vmid').value;
        $.ajax({
          url: '/baadal/action/index.json',
          type: 'post',
          data: {
            vmid: vmid,
            action: 'restore-snapshot',
            snapshot_id: this.closest('tr').getAttribute('data-snapshot-id')
          },
          success: function(response) {
              if (response.message) {
                  $('#modal-info-message').html(response.message).fadeIn().siblings().hide();
              }
          }
        });
      });

      $(document.body).on('click', '.snapshot-delete', function (e) {
        var vmid = document.getElementById('vmid').value;
        $.ajax({
          url: '/baadal/action/index.json',
          type: 'post',
          data: {
            vmid: vmid,
            action: 'delete-snapshot',
            snapshot_id: this.closest('tr').getAttribute('data-snapshot-id')
          },
          success: function(response) {
              if (response.message) {
                  $('#modal-info-message').html(response.message).fadeIn().siblings().hide();
              }
          }
        });
      });


      $(document.body).on('click', '#fetch-snapshots', function (e) {
        var $tr = $(this),
          vmid = document.getElementById('vmid').value;
        $.ajax({
          url: '/baadal/ajax/snapshots.json',
          type: 'post',
          data: {
            vmid: vmid
          },
          success: function (response) {
            var html = baadalApp.populateSnapshots(response.data, document.getElementById('snapshots-tmpl').innerHTML);
            $tr.closest('tbody').html(html);
          },
          error: function (error, response, code) {
            console.log(error, response, code);
          }
        });
      });

      $this.table.on('click', '.btn-action', function (e) {
        var id = this.closest('tr').getAttribute('data-vmid'),
          action = this.getAttribute('data-action'),
          tooltip,
          span = this.children[0];
        if (action === 'start') {
          tooltip = 'Starting...';
        } else {
          tooltip = 'Stopping...';
        }
        this.title = tooltip;
        span.classList.remove('fa-play', 'fa-stop');
        span.classList.add('fa-refresh', 'fa-spin');
        $.ajax({
          'url': '/baadal/action/index.json',
          'type': 'post',
          'dataType': 'json',
          'data': {
            'vmid': id,
            'action': action
          },
          'error': function (response) {
            var error = response.getResponseHeader('web2py_error');
            if (error) {
              baadalApp.generateTicketLink(error);
            }
          },
          'success': function (response) {
            if (response.status === 'success') {
              $('#success-message').fadeIn(1000, function () {
                $this.$dt.ajax.reload();
                $(this).fadeOut();
              });
            } else {
              $('#error-message').fadeIn();
            }
          }
        });
        return baadalApp;
      });
    }
  };
  return baadalApp;
}(jQuery));

if (Handlebars) {
  Handlebars.registerHelper('ifCond', function (v1, operator, v2, options) {
    'use strict';
    switch (operator) {
    case '==':
      return (v1 == v2) ? options.fn(this) : options.inverse(this);
    case '===':
      return (v1 === v2) ? options.fn(this) : options.inverse(this);
    case '<':
      return (v1 < v2) ? options.fn(this) : options.inverse(this);
    case '<=':
      return (v1 <= v2) ? options.fn(this) : options.inverse(this);
    case '>':
      return (v1 > v2) ? options.fn(this) : options.inverse(this);
    case '>=':
      return (v1 >= v2) ? options.fn(this) : options.inverse(this);
    case '&&':
      return (v1 && v2) ? options.fn(this) : options.inverse(this);
    case '||':
      return (v1 || v2) ? options.fn(this) : options.inverse(this);
    default:
      return options.inverse(this);
    }
  });
}
