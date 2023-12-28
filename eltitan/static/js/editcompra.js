// Variable global para almacenar el índice del producto seleccionado
var selectedProductIndex;
var tblProducts;
var vents = {
    items: {
        numFactura: '',
        fechaFactura: '',
        fechaCompra: '', // Capture fechaCompra
        total: 0.00, // Obtiene el valor del total

        products: [],
        addedProducts: [],
    },
    add: function (item) {

        // Calculate the total amount
        var costo = item.cant * item.precio;
        // Add the total amount to the item
        item.costo = costo;
        this.items.products.push(item);
        this.items.addedProducts.push(item);
        tblProducts.row.add(item).draw();
        // Calculate and display the total
        var total = this.calculateTotal();
        document.getElementById('total').innerHTML = total;
    },
    calculateTotal: function () {
        var total = 0.00;
        for (var i = 0; i < this.items.products.length; i++) {
            total += this.items.products[i].costo;
        }
        return total;
    },
    list: function () {

        console.log('Updated list of products:', this.items.products);
        tblProducts = $('#tblProducts').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            data: this.items.products,
            columns: [
                { "data": "name" },
                { "data": "cant" },
                {
                    "data": "precio", render: function (data, type, row) {
                        return parseFloat(data).toFixed(2);
                    }
                },
                {
                    "data": "costo", render: function (data, type, row) {
                        return parseFloat(data).toFixed(2);
                    }
                },
                { "data": "id" },


            ],
            columnDefs: [
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row, meta) {
                        // Agregar el botón de edición junto al botón de eliminación
                        return '<a rel="edit" class="btn btn-warning btn-xs btn-flat m-3" style="color: white; margin-left: 5px;" data-toggle="modal" data-target="#editModal" data-index="' + meta.row + '"><i class="fas fa-pencil-alt"></i></a>' +
                            '<a rel="remove" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-trash-alt"></i></a>';
                    }

                },


            ],
            rowCallback(row, data, displayNum, displayIndex, dataIndex) {

            },

        });
        console.clear();
        console.log(this.items);
    },

};
function getIndexByProductName(productName) {
    for (var i = 0; i < vents.items.products.length; i++) {
        if (vents.items.products[i].name === productName) {
            return i;
        }
    }
    return -1;
}

function checkIfProductExists(productName) {
    for (var i = 0; i < vents.items.products.length; i++) {
        if (vents.items.products[i].name === productName) {
            return true;
        }
    }
    return false;
}
function formatRepo(repo) {
    if (repo.loading) {
        return repo.text;
    }

    var badgeClass = repo.cant_dis > 0 ? "badge-success" : "badge-danger";

    var option = $(
        '<div class="container">' +
        '<div class="row">' +
        '<div class="col-lg-1"></div>' +
        '<div class="col-lg-11 text-left shadow-sm">' +
        '<p style="margin-bottom: 0;">' +
        '<b>Nombre:</b> ' + repo.name + '<br>' +
        '<b>Categoría:</b> ' + repo.cat.name + '<br>' +
        '<b>Precio de venta:</b> <span class="badge badge-warning">$' + repo.precio_venta + '</span>' + '<br>' +
        '<b>Cantidad en existencia:</b> <span class="badge ' + badgeClass + ' ">' + repo.cant_dis + '</span>' +
        '</p>' +
        '</div>' +
        '</div>' +
        '</div>');

    return option;
}


$(function () {

    $('.btnRemoveAll').on('click', function () {
        if (vents.items.products.length === 0) return false;
        vents.items.products = [];
        vents.items.addedProducts = [];
        vents.list();
        var total = vents.calculateTotal();
        document.getElementById('total').innerHTML = total;
    });

    $('#tblProducts tbody')
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products.splice(tr.row, 1);
            vents.items.addedProducts.splice(tr.row, 1); // Añade esta línea
            vents.list();
            var total = vents.calculateTotal();
            document.getElementById('total').innerHTML = total;
        })
        .on('click', 'a[rel="edit"]', function () {
            // Almacenar el índice del producto en la variable global
            selectedProductIndex = $(this).data('index');

            // Obtener el producto seleccionado
            var selectedProduct = vents.items.products[selectedProductIndex];

            // Actualizar los valores en el modal de edición
            $('#editQty').val(selectedProduct.cant);
            $('#editPrice').val(selectedProduct.precio);
        });





    $('.btnClearSearch').on('click', function () {
        $('input[name="search"]').val('').focus();
    });


    $('#edit').on('submit', function (e) {
        e.preventDefault();

        // Prevent form submission if there are no products

        console.log('hola estoy en eleditar');

        // Get the values from the form fields
        vents.items.numFactura = $('#numFactura').val();
        vents.items.fechaFactura = $('#fechaFactura').val();
        vents.items.fechaCompra = $('#fechaCompra').val(); // Capture fechaCompra
        vents.items.total = $('#total').text(); // Obtiene el valor del total


        // Create a new FormData object
        var parameters = new FormData();

        parameters.append('vents', JSON.stringify(vents.items));


        // Send the AJAX request
        $.ajax({
            url: '/inventarios/editar/',
            type: 'POST',
            data: parameters,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function (response) {
                // Handle the response from the server

                console.log(response);
                location.href = '/inventarios/listarCompra/ ';

            },
            error: function (jqXHR, textStatus, errorThrown) {
                // Handle any errors
                console.error(textStatus, errorThrown);
            }
        });
    });



    $('select[name="search"]').select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: '/inventarios/buscar_producto/',
            data: function (params) {
                var queryParameters = {
                    term: params.term,
                    action: 'search_products'
                }
                return queryParameters;
            },
            processResults: function (data) {
                // Filtra los resultados para excluir los productos que ya han sido agregados
                var filteredResults = data.filter(function (product) {
                    return !vents.items.addedProducts.some(function (addedProduct) {
                        return addedProduct.name === product.name;
                    });
                });
                // Si todos los resultados fueron filtrados, muestra un mensaje personalizado
                if (filteredResults.length === 0 && data.length > 0) {
                    alert('El producto ya ha sido agregado a la lista o no existe.');
                }
                return {
                    results: filteredResults
                };
            },
            headers: {
                'X-CSRFToken': csrftoken
            }
        },
        placeholder: 'Elige los productos que vas a comprar',
        minimumInputLength: 1,
        templateResult: formatRepo,
    })

    $('select[name="search"]').on('select2:select', function (e) {
        var selectedProduct = e.params.data.name;
        console.log('prueba de selectedProduct', selectedProduct);
        selectedProductIndex = getIndexByProductName(selectedProduct);
        var productExists = checkIfProductExists(selectedProduct);

        if (productExists) {
            // Obtener el índice del producto existente en la tabla
            var existingProductIndex = getIndexByProductName(selectedProduct);

            if (existingProductIndex !== -1) {
                // Obtener los datos del producto existente
                var existingProduct = vents.items.products[existingProductIndex];

                // Actualizar los valores en el modal de edición
                $('#editQty').val(existingProduct.cant);
                $('#editPrice').val(existingProduct.precio);

                // Mostrar el modal de edición
                $('#editModal').modal('show');
            }

            console.log("El producto ya existe en la tabla");
            // Clear the select value
            $(this).val(null).trigger('change');
        } else {
            console.log("El producto no existe en la tabla");
        }


    });



    $.ajax({
        url: '/inventarios/editar/',
        type: 'GET',
        success: function (data) {
            // Imprime los datos recibidos
            console.log(data);

            // Llena los campos de entrada con los datos obtenidos
            $('#numFactura').val(data.numFactura);
            $('#fechaFactura').val(data.fechaFactura);
            $('#fechaCompra').val(data.fechaCompra);
            $('#total').text(data.total);

            // Llena la tabla de productos con los datos recibidos
            vents.items.products = data.detalles;
            vents.list();



        }
    });

    $('#saveBtn').click(function () {
        var qty = $('#editQty').val();
        var price = $('#editPrice').val();

        if (typeof selectedProductIndex !== 'undefined' && selectedProductIndex >= 0 && selectedProductIndex < vents.items.products.length) {
            // Recalculate totalAmount
            var totalAmount = qty * price;
            // Update cant, precio, and totalAmount
            vents.items.products[selectedProductIndex].cant = qty;
            vents.items.products[selectedProductIndex].precio = price;
            vents.items.products[selectedProductIndex].costo = totalAmount;
            vents.list();
            var total = vents.calculateTotal();
            document.getElementById('total').innerHTML = total;

            // Hide the modal
            $('#editModal').modal('hide');
        } else {
            console.error("Invalid index: ", selectedProductIndex);
        }
    });

    $('#agregar').click(function () {
        var productName = $('#productSearch').find('option:selected').text();
        var productPrice = $('#productPrice').val();
        var productQuantity = $('#productQuantity').val();
        // Check if productPrice exists and is not empty
        if (!productPrice) {
            console.error('Product price is not defined');
            return;
        }

        // Parse productPrice to a number if it's supposed to be a number
        var parsedProductPrice = parseFloat(productPrice);
        if (isNaN(parsedProductPrice)) {
            console.error('Invalid product price');
            return;
        }
        var data = {
            id: '',
            name: productName,
            precio: productPrice,
            cant: productQuantity
        };

        // Your existing code...
        console.log('Adding new product:', data);
        vents.add(data);

        // Clear the form inputs
        $('#productSearch').val(null).trigger('change');
        $('#productPrice').val('');
        $('#productQuantity').val('');
    });

    vents.list();
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');