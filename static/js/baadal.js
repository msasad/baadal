function serialize(temp) {
    var obj = {};
    for (i in temp) {
        curr = temp[i];
        obj[curr.name] = curr.value;
    }
    return obj;
}

function generateTicketLink(error) {
  //web2py_error:"ticket baadal/127.0.0.1.2015-10-13.16-48-16.fac5ead6-a412-4bf7-ade3-f4d01566fa39"
  //http://127.0.0.1:8000/admin/default/ticket/baadal/127.0.0.1.2015-10-13.16-48-16.fac5ead6-a412-4bf7-ade3-f4d01566fa39
  console.log('http://127.0.0.1:8000/admin/default/ticket/' + error.split(' ')[1]);
}