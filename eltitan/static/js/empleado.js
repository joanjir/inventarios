$(document).ready(function () {

    // Evento del botón eliminar .eliminar-btn
    $(document).on('click', '.eliminarEmpleado', function (event) {
        var objetoId = $(this).data('id');

        Swal.fire({
            title: '¿Estás seguro de eliminar al empleado?',
            text: 'Esta acción no se podra revertir',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Aceptar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.value) {
                var csrfToken = getCookie('csrftoken');
                $.ajax({
                    url: '/administraciones/eliminarEmpleado/' + objetoId + '/',
                    type: 'POST',
                    headers: { 'X-CSRFToken': csrfToken },
                    success: function (response) {
                        // Eliminar el card correspondiente al empleado eliminado
                        $('.eliminarEmpleado[data-id="' + objetoId + '"]').closest('.col-12').remove();
                        toastr.success('¡Eliminado! ' + response.mensaje, '', { timeOut: 1000 });

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


    
})

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