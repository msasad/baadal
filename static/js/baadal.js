var baadalApp = Object();
baadalApp.serialize = function (temp) {
  var obj = {};
  for (var i in temp) {
    var curr = temp[i];
    obj[curr.name] = curr.value;
  }
  return obj;
};

baadalApp.generateTicketLink = function(error) {
  console.log('http://127.0.0.1:8000/admin/default/ticket/' + error.split(' ')[1]);
};

baadalApp.ipArrayToString = function(data, usebr) {
  if (typeof data == 'string') return data;
  var arr = [];
  for (var i = data.length - 1; i>=0; i--) {
    var str = '';
    var keys = Object.keys(data[i]);
    for (var j = keys.length - 1; j >= 0; j--) {
      str += keys[j] + ':' + data[i][keys[j]] + ' ';
    }
    arr.push(str);
  }
  return arr.join(usebr ? '<br>' : '\n');
};

baadalApp.ipObjectToString = function(object) {
  strings = [];
  for (var i in object) {
    ips = object[i];
    for (var ip of ips) {
      strings.push('MAC: ' + ip['OS-EXT-IPS-MAC:mac_addr'] + ' IP: ' + ip['addr']);
    }
  }
  return strings.join('<br/>')
};

if (Handlebars) {
  Handlebars.registerHelper('ifCond', function (v1, operator, v2, options) {
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

baadalApp.filterArrayObject = function(object, array_name, field_name, value) {
  if (object.hasOwnProperty(array_name)) {
    var array = object[array_name];
    var newarray = [];
    for ( var a in array) {
      if (array[a][field_name] == value) {
        newarray.push(array[a]);
      }
    }
  }
  object[array_name] = newarray;
  return object;
};

baadalApp.getSettingsButtonsMarkup = function(status) {
   var actions = {
     'ACTIVE' : 'shutdown',
     'SHUTOFF' : 'start',
     'ERROR' : 'start'
   };

   var glyphicons = {
     'ACTIVE' : 'stop',
     'SHUTOFF' : 'play',
     'ERROR' : 'play'
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
}
