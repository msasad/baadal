/*global

console,
Handlebars
*/

var baadalApp = (function () {
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
    console.log(document.location.origin + '/admin/default/ticket/' + error.split(' ')[1]);
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
    return '<div class="btn-group" role="group" aria-label="..."><button title="' +
      actions[status] +
      '" type="button" data-action="' +
      actions[status] +
      '" class="btn btn-success btn-action" aria-label="Start"><span class="fa fa-' +
      glyphicons[status] +
      '" aria-hidden="true"></span></button><button title="Settings" type="button"' +
      'data-action="settings" class="btn btn-primary btn-settings" aria-label="Settings">' +
      '<span class="fa fa-cog" aria-hidden="true"></span></button></div>';
  };
  return baadalApp;
}());

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