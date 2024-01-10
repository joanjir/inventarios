$(document).ready(function () {
    // Crear la tabla con DataTables
    var table = $('#data').DataTable({

    });

    

    // Evento del botón eliminar .eliminar-btn
    $(document).on('click', '.eliminar-btn', function (event) {
        var objetoId = $(this).data('objeto-id');

        var estado = $(this).data('estado');

        if (estado === 'ANU') {
            return;
        }
        Swal.fire({
            title: '¿Estás seguro de anular la compra?',
            text: 'Esta acción también disminuye la existencia de los productos',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Anular',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.value) {
                var csrfToken = getCookie('csrftoken');
                $.ajax({
                    url: '/eliminar_compra/' + objetoId + '/',
                    type: 'POST',
                    headers: { 'X-CSRFToken': csrfToken },
                    success: function (response) {
                        toastr.success('¡Anulado! ' , '', { timeOut: 2000 });

                        setTimeout(function () {
                            window.location.reload();
                        }, 1000); // Espera 3 segundos antes de recargar la página
                    },
                    error: function (xhr) {
                        toastr.error('Error: ' + xhr.responseJSON.mensaje, '', { timeOut: 2000 });
                    }
                });
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











