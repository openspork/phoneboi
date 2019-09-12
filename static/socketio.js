


$(document).ready(function() {
    namespace = '/test';

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
        socket.emit('my_event', {data: 'I\'m connected!'});
    });

    socket.on('heartbeat', function(msg) {
        heatbeat_time = Date(msg.datetime)
        $('#heartbeat').text('Received #' + msg.count + ': ' + heatbeat_time);
    });

    socket.on('log', function(msg) {
        $('#log').append('<br>' + $('<div/>').text('Received ' + msg.type + ': ' + msg.data).html());
    });

    // Send updates
    $('.update').click(function(event) {
        guid = $(this).attr('id');
        alert(guid);
        socket.emit('update', {data: guid});

        // $('#log').prepend(`
        //     <tr class=${guid}_tr>
        //         <td>${hash}</td>
        //         <td>${queryCmd}</td>
        //         <td id='${guid}_result''>?</td>
        //         <td><button>Fav.</button></td> 
        //     </tr>
        //     `);
    });

    // Handle query response
    socket.on('query_resp', function(msg) {
        hash = msg.hash
        guid = msg.guid
        code = msg.code
        result = msg.result
        $(`#${guid}_result`).text(result);
    });

    socket.on('inventory', function(msg) {
        alert('Inventory update: ' + msg.data)
    });
});