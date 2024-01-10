$(document).ready(function () {
    var table = $('#data').DataTable({});
    var btn = $('.moverBtn');
    btn.click(function () {
        var inventarioId = $(this).data('inventario-id');
        cantidad_existente = $(this).data('cantidad-existente');
        $('#inventario_id').val(inventarioId);
        $('#cantidad_existente').val(cantidad_existente);
        $('#myModal').modal('show');
        $('#cantidad').val('');

    });

    $('#moveForm').on('submit', function (event) {
        event.preventDefault();
        var cantidad = parseInt($('#cantidad').val());
        cantidad = cantidad + ',00';
        var cantidad_existente = parseInt($('#cantidad_existente').val());
        if (cantidad <= 0 || cantidad > cantidad_existente || !cantidad) {
            $('#cantidadError').text('La cantidad debe ser mayor que cero y no puede ser mayor que la cantidad en stock.').show();
            return;
        }
        var formData = $(this).serializeArray();
        var csrftoken = getCookie('csrftoken');
        var inventarioId = $('#inventario_id').val();
        var url = '/mover_inventario/' + inventarioId + '/';
        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: formData,
            success: function (response) {
                if (response.errors) {
                    // Display errors
                    for (var field in response.errors) {
                        var errorSpan = document.getElementById(field + 'Error');
                        if (errorSpan) {
                            errorSpan.textContent = response.errors[field];
                        }
                    }
                } else {
                    console.log(response);

                    $('#myModal').modal('hide');
                    window.location.reload();



                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
                var errorMessage = jqXHR.responseJSON ? jqXHR.responseJSON.detail : 'An error occurred.';
                toastr.error(errorMessage);
            }
        });
    });

});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
