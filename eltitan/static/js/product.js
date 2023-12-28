$(document).ready(function () {
    // Crear la tabla con DataTables
    var table = $('#data').DataTable({

    });


    //Evento del boton eliminar .eliminar-btn
    $(document).on('click', '.eliminar-btn', function (event) {
        var objetoId = $(this).data('objeto-id');

        event.preventDefault();

        $.ajax({
            url: '/inventarios/verificarCategoria/' + objetoId + '/',
            type: 'GET',
            success: function (response) {
                if (response.mensaje === 'La categoria tiene productos asociados y no puede ser eliminada.') {
                    // Display a message on the button
                    toastr.warning('La categoría tiene productos asociados y no puede ser eliminada.');

                } else {
                    Swal.fire({
                        title: '¿Estás seguro de eliminar el registro?',
                        text: 'Esta acción también elimina completamente la categoría',
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#d33',
                        cancelButtonColor: '#3085d6',
                        confirmButtonText: 'Eliminar',
                        cancelButtonText: 'Cancelar'
                    }).then((result) => {
                        if (result.value) {
                            $.ajax({
                                url: '/inventarios/eliminarCategoria/' + objetoId + '/',
                                type: 'POST',
                                success: function (response) {
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
                }
            },
            error: function (xhr) {
                toastr.error('Error: ' + xhr.responseJSON.mensaje, '', { timeOut: 2000 });
            }
        });


    });


});