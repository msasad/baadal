/*global

console,
Handlebars,
jQuery
*/

var baadalApp = (function ($) {
  'use strict';
  baadalApp = {};
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

      var promise = $.get(this.templateURL),
        $this = this;
      promise.then(function (response) {
        $this.dialogTmpl = Handlebars.compile(response);
      });
    },
    setupTable: function (isAdmin) {
      var dataURL = this.dataURL,
        emptyMsg = "You don't have any VMs currently! You may request" +
              "one <a href=\"./form\">here</a>",
        columns,
        $dt;
      columns = isAdmin ? [
        { "data": "name" },
        { "data": "status" },
        { "data": "user_id" },
        { "data": "flavor.id" },
        { "data": "image.info" },
        { "data": null },
        { "data": "OS-EXT-SRV-ATTR:instance_name"  },
        { "data": "OS-EXT-SRV-ATTR:host" },
        { "data": null }
      ] : [
        { "data": "name" },
        { "data": "status" },
        { "data": "user_id" },
        { "data": "flavor.id" },
        { "data": "image.info" },
        { "data": null },
        { "data": null }
      ];

      this.$dt = this.table.DataTable({
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
        actionbtn = '#' + $this.modalid + ' .btn-action';

      // Event handler for click of settings button
      $this.table.on('click', '.btn-settings', function (e) {
        var tr = this.closest('tr'),
          context = $this.$dt.row(tr).data(),
          html;
        context['ip-addresses'] = baadalApp.ipObjectToString(context.addresses,       true);
        html = $this.dialogTmpl(context);
        $(document.body).prepend(html);
        $this.$modal = $('#' + $this.modalid).modal('show');
        $this.$modal.on('hidden.bs.modal', function () {
          $this.$modal.remove();
          $this.$dt.ajax.reload();
        });
        $this.$modal.footer = $this.$modal.find('.panel-footer');
      });

      // Event handler for click of action buttons on settings dialog
      $(document.body).on('click', actionbtn, function () {
        var vmid = $(this).parent.data('vmid'),
          action = $(this).data('action'),
          buttons_html = '<span>Do you really want to delete this VM? This action cannot be undone!</span> <button type="button" name="btn-yes"            class="btn btn-danger" data-confirm="yes">Yes</button>            <button type="button" name="btn-no" class="btn btn-success"            data-confirm="no">No</button>',
          html,
          span,
          flavor_selector;
          // var vmid = this.parentElement.getAttribute('data-vmid');
          // var action = this.getAttribute('data-action');
        if (action === 'delete') {
          $this.$modal.footer.html(buttons_html).slideDown(function () {

            this.children.namedItem('btn-no').addEventListener('click', function () {
              $this.$modla.footer.slideUp().html('');
            });
            this.children.namedItem('btn-yes').addEventListener('click', function () {
              $.ajax({
                url: '/baadal/action/index.json',
                type: 'post',
                data: {
                  'vmid': vmid,
                  'action': action
                },
                'error': function (response) {
                  var error = response.getResponseHeader('web2py_error');
                  if (error) {
                    baadalApp.generateTicketLink(error);
                  }
                },
                success: function (response) {
                  var message;
                  switch (action) {
                  case 'get-console-url':
                    message = '<a target="_blank" href="' + response.consoleurl +
                      '">' + response.consoleurl + '</a>';
                    break;
                  case 'snapshot':
                    message = 'Snapshot creation has been initiated.';
                    break;
                  case 'start-resume':
                    message = 'Start/resume action has been queued. Please wait' +
                      ' while your VM starts';
                    break;
                  case 'shutdown':
                    message = 'VM stop action has been queued. Please wait while' +
                      'your VM is shut down.';
                    break;
                  case 'clone':
                    message = 'Clone request has been posted.';
                    break;
                  }
                  $this.$modal.footer.show();
                  $this.$modal.find('#modal-info-message').html(message).slideDown();
                }
              });
              $this.$modal.footer.slideUp().html('');
            });
          });
        } else if (action === 'add-virtual-disk') {
          html = '<form class="form-inline" action="#"> ' +
            '<div class="form-group"> ' +
            '<label for="disksize" class="control-label"> ' +
            'Disk size</label> ' +
            '<input type="number" class="form-control" name="disksize" id="disksize" ' +
            'value="1" max="1024" min="1" /> ' +
            '</div> <button class="btn btn-primary btn-sm" id="btn-disk-request"> ' +
            'Submit Request </button> </form> ';
          $this.$modal.footer.html(html);
          $('#btn-disk-request').on('click', function (e) {
            e.preventDefault();
            $.ajax({
              url: '/baadal/action/index.json',
              data: {
                'vmid': vmid,
                action: 'add-virtual-disk',
                disksize: document.getElementById('disksize').value
              },
              success: function (response) {
                if (response.status === 'success') {
                  $this.$modal.footer.html(
                    '<p class="text-info"> Request posted successfully. ' +
                      'Extra disk will be added to the VM when the request ' +
                      'will be approved by admin </p>'
                  );
                }
              }
            });
          });
          $this.modal.footer.slideDown();
        } else if (action === 'resize') {
          flavor_selector = document.getElementById('new_flavor');
          html = '<form class="form-inline" action="#"> ' +
                ' <label for="new_flavor" class="control-label"> ' +
                'Select new configuration</label> ' +
                ' <select class="form-control" name="new_flavor" id="new_flavor"> </select> ' +
                ' <button class="btn btn-primary btn-sm" id="btn-resize-request"> Submit Request' +
                '</button> </form>';
          $this.$modal.footer.html(html);
          $.ajax({
            url: '/baadal/ajax/configs.json',
            dataType: 'json',
            success: function (response) {
              response.forEach(function (flavor, index) {
                flavor_selector.options.add(new Option(flavor.vcpus + 'CPU, ' +
                      flavor.ram + 'MB RAM', flavor.id));
              });
              $('#btn-resize-request').on('click', function (e) {
                e.preventDefault();
                $.ajax({
                  url: '/baadal/post_request/request_resize.json',
                  type: 'post',
                  data: {
                    'vmid': vmid,
                    // name: context.name,
                    name:  undefined,
                    new_flavor: flavor_selector.value
                  },
                  success: function (response) {
                    var span = document.createElement('span');
                    if (response.status === 'success') {
                      span.classList.add('text-success');
                      span.innerHTML = 'Request posted successfully';
                      $this.$modal.footer.html(span);
                    } else {
                      span = document.createElement('span');
                      span.classList.add('text-danger');
                      span.innerHTML = 'There was some error in posting the request.';
                      $this.$modal.footer.html(span);
                    }
                  },
                  'error': function (response) {
                    var error = response.getResponseHeader('web2py_error');
                    if (error) {
                      baadalApp.generateTicketLink(error);
                    }
                  }
                });
                return false;
              });
              $this.$modal.footer.slideDown();
            },
            'error': function (response) {
              var error = response.getResponseHeader('web2py_error');
              if (error) {
                baadalApp.generateTicketLink(error);
              }
            }
          });
        } else {
          $.ajax({
            url: '/baadal/action/index.json',
            type: 'post',
            data: {
              'vmid': vmid,
              'action': action
            },
            'error': function (response) {
              var error = response.getResponseHeader('web2py_error');
              if (error) {
                baadalApp.generateTicketLink(error);
              }
            },
            success: function (response) {
              var message;
              switch (action) {
              case 'get-console-url':
                message = '<a target="_blank" href="' + response.consoleurl +
                  '">' + response.consoleurl + '</a>';
                break;
              case 'snapshot':
                message = 'Snapshot creation has been initiated.';
                break;
              case 'start-resume':
                message = 'Start/resume action has been queued. Please wait ' +
                  'while your VM becomes ready.';
                break;
              case 'shutdown':
                message = 'VM stop action has been queued. Please wait while  ' +
                  'your VM is shut down.';
                break;
              case 'clone':
                message = 'Clone request has been posted.';
                break;
              }
              $this.$modal.footer.show();
              $this.$modal.find('#modal-info-message').html(message).slideDown();
            }
          });
        }
      });

      // Event handler for snapshot-restore buttons
      $(document.body).on('click', '#' + $this.modalid + '.snapshot-restore', function (e) {
        var vmid = document.getElementById('vmid').value;
        $.ajax({
          url: '/baadal/action/index.json',
          type: 'post',
          data: {
            vmid: vmid,
            action: 'restore-snapshot',
            snapshot_id: this.closest('tr').getAttribute('data-snapshot-id')
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
