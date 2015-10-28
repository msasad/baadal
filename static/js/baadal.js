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
  var str = '';
  for (var i = data.length - 1; i>=0; i--) {
    var keys = Object.keys(data[i]);
    for (var j = keys.length - 1; j >= 0; j--) {
      str += keys[j] + ':' + data[i][keys[j]] + ' ';
    }
    if (usebr) {
      str += '<br>';
    } else {
      str += '\n';
    }
  }
  return str;
}