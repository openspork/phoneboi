


$(document).ready(function() {
    namespace = '/test';

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
        socket.emit('my_event', {data: 'I\'m connected!'});
    });



    socket.on('log', function(msg) {
        $('#log').append('<br>' + $('<div/>').text('Received ' + msg.type + ': ' + msg.data).html());
    });

    // Send updates
    $('.update').click(function(event) {
        guid = $(this).attr('id');
        socket.emit('update', {data: guid});

        $('#log').prepend(`
            <tr>
                <td>${guid}</td>
                <td>asdf</td>
            </tr>
            `);
    });


    socket.on('inventory', function(msg) {
        alert('Inventory update: ' + msg.data)
    });

    socket.on('heartbeat', function(msg) {
        heatbeat_time = Date(msg.datetime)
        $('#heartbeat').text('Received #' + msg.count + ': ' + heatbeat_time);
    });

});