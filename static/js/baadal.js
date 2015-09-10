function serialize(temp) {
    var obj = {};
    for (i in temp) {
        curr = temp[i];
        obj[curr.name] = curr.value;
    }
    return obj;
}