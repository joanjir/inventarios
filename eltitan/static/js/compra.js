// Variable global para almacenar el índice del producto seleccionado
var selectedProductIndex;
var tblProducts;
var totalStr;
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
        var totalAmount = item.cant * item.precio;
        // Add the total amount to the item
        item.totalAmount = totalAmount;
        this.items.products.push(item);
        this.items.addedProducts.push(item);
        tblProducts.row.add(item).draw();
        // Cuando calculas el total
        var total = this.calculateTotal();

        // Convierte el total a una cadena con dos decimales
        totalStr = total.toFixed(2);
        // Muestra el total en el HTML
        document.getElementById('total').innerHTML = totalStr;
    },
    calculateTotal: function () {
        var total = 0.00;
        for (var i = 0; i < this.items.products.length; i++) {
            total += this.items.products[i].totalAmount;
        }
        return parseFloat(total.toFixed(2));
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
                    "data": "totalAmount", render: function (data, type, row) {
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
    $('#productSearchError').text('');
    $('#productSearch').removeClass('is-invalid');
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
        // Convierte el total a una cadena con dos decimales
        var totalStr = total.toFixed(2);

        document.getElementById('total').innerHTML = totalStr;
    });

    $('#tblProducts tbody')
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products.splice(tr.row, 1);
            vents.items.addedProducts.splice(tr.row, 1); // Añade esta línea
            vents.list();
            var total = vents.calculateTotal();
            // Convierte el total a una cadena con dos decimales
            var totalStr = total.toFixed(2);

            document.getElementById('total').innerHTML = totalStr;
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

    toastr.options = {
        "preventDuplicates": true
    };


    $('form').on('submit', function (e) {
        e.preventDefault();
        // Check if there are no products
        if (vents.items.products.length === 0) {
            toastr.warning('No se puede efectuar la compra sin al menos un producto agregado.');
        }


        var numFactura = $('#numFactura').val();
        var fechaFactura = $('#fechaFactura').val();
        var fechaCompra = $('#fechaCompra').val();

        if (!numFactura) {
            $('#numFacturaError').text('Por favor complete No. Factura');
            $('#numFactura').addClass('is-invalid');
        } else {
            $('#numFacturaError').text('');
            $('#numFactura').removeClass('is-invalid');
        }
        if (!fechaFactura) {
            $('#fechaFacturaError').text('Por favor complete Fecha factura');
            $('#fechaFactura').addClass('is-invalid');
        } else {
            $('#fechaFacturaError').text('');
            $('#fechaFactura').removeClass('is-invalid');
        }
        if (!fechaCompra) {
            $('#fechaCompraError').text('Por favor complete Fecha de compra');
            $('#fechaCompra').addClass('is-invalid');
        } else {
            $('#fechaCompraError').text('');
            $('#fechaCompra').removeClass('is-invalid');
        }

        // Only prevent form submission if there are validation errors
        if ($('.is-invalid').length > 0 || vents.items.products.length === 0) {
            toastr.error('Aún quedan errores de validación');
            e.preventDefault();
        } else {
            // Get the values from the form fields
            vents.items.numFactura = $('#numFactura').val();
            vents.items.fechaFactura = $('#fechaFactura').val();
            vents.items.fechaCompra = $('#fechaCompra').val(); // Capture fechaCompra
            vents.items.total = parseFloat($('#total').text()).toString(); // Obtiene el valor del total
            // Create a new FormData object
            var parameters = new FormData();
            parameters.append('vents', JSON.stringify(vents.items));

            // Send the AJAX request
            $.ajax({
                url: '/guardar_compra/',
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
                    location.href = '/listarCompra/ ';
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    // Handle any errors
                    console.error(textStatus, errorThrown);
                }
            });
        }
    });





    $('select[name="search"]').select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: '/buscar_producto/',
            data: function (params) {
                var queryParameters = {
                    term: params.term,
                    action: 'search_products'
                }
                return queryParameters;
            },
            processResults: function (data) {
                // Iterar sobre cada producto en la lista de resultados
                for (var i = 0; i < data.length; i++) {
                    // Si el producto ya ha sido añadido, marcarlo como seleccionado
                    if (vents.items.addedProducts.some(function (addedProduct) {
                        return addedProduct.name === data[i].name;
                    })) {
                        data[i].selected = true;
                    }
                }
                return {
                    results: data
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
            $('#productSearchError').text('');
            $('#productSearch').removeClass('is-invalid');


            console.log("El producto ya existe en la tabla");
            // Clear the select value
            $(this).val(null).trigger('change');
        } else {
            $('#productSearchError').text('');
            $('#productSearch').removeClass('is-invalid');
            console.log("El producto no existe en la tabla");
        }
    });





    $('#saveBtn').click(function () {
        var qty = $('#editQty').val();
        var price = $('#editPrice').val();

        // Verificar si los campos son válidos
        if ($('#editQty')[0].checkValidity() && $('#editPrice')[0].checkValidity()) {
            // Tu código existente...
            if (typeof selectedProductIndex !== 'undefined' && selectedProductIndex >= 0 && selectedProductIndex < vents.items.products.length) {
                // Recalculate totalAmount
                var totalAmount = qty * price;
                // Update cant, precio, and totalAmount
                vents.items.products[selectedProductIndex].cant = qty;
                vents.items.products[selectedProductIndex].precio = price;
                vents.items.products[selectedProductIndex].totalAmount = totalAmount;
                vents.list();
                // Cuando calculas el total
                var total = vents.calculateTotal();

                // Convierte el total a una cadena con dos decimales
                var totalStr = total.toFixed(2);

                // Muestra el total en el HTML
                document.getElementById('total').innerHTML = totalStr;


                // Hide the modal
                $('#editModal').modal('hide');
                $('#productSearchError').text('');
                $('#productSearch').removeClass('is-invalid');

                // Clear the product selection error message and mark the field as valid
                $('#productSearchError').text('');
                $('#productSearch').removeClass('is-invalid');

                // Clear the product price error message and mark the field as valid
                $('#productPriceError').text('');
                $('#productPrice').removeClass('is-invalid');

                // Clear the product quantity error message and mark the field as valid
                $('#productQuantityError').text('');
                $('#productQuantity').removeClass('is-invalid');
            } else {
                console.error("Invalid index: ", selectedProductIndex);
            }
        } else {
            // Marca el formulario como inválido si la validación falla
            $('#editForm')[0].classList.add('was-validated');
        }
    });






    $('#productPrice').on('input', function () {
        validateProductPrice();
    });

    $('#productQuantity').on('input', function () {
        validateProductQuantity();
    });

    $('#productSearch').on('change', function () {
        validateProductName();
    });



    $('#agregar').click(function () {
        // Validate the other fields
        validateProductName();
        validateProductPrice();
        validateProductQuantity();

        // Only proceed if all fields are valid
        if (validateProductName() && validateProductPrice() && validateProductQuantity()) {
            var data = {
                id: '',
                name: $('#productSearch').find('option:selected').text(),
                precio: $('#productPrice').val(),
                cant: $('#productQuantity').val()
            };

            console.log('Adding new product:', data);
            vents.add(data);

            // Clear the form inputs
            $('#productSearch').val(null).trigger('change');
            $('#productPrice').val('');
            $('#productQuantity').val('');

            // Clear the product selection error message and mark the field as valid
            $('#productSearchError').text('');
            $('#productSearch').removeClass('is-invalid');

            // Clear the product price error message and mark the field as valid
            $('#productPriceError').text('');
            $('#productPrice').removeClass('is-invalid');

            // Clear the product quantity error message and mark the field as valid
            $('#productQuantityError').text('');
            $('#productQuantity').removeClass('is-invalid');
        }
    });


    vents.list();
});

function clearError(errorId) {
    // Clear the error message
    $('#' + errorId).text('');

    // Remove the is-invalid class from the corresponding input field
    var inputFieldId = errorId.slice(0, -5); // Removes 'Error' from the end of the string
    $('#' + inputFieldId).removeClass('is-invalid');
}

function checkIfProductExists(productName) {
    return vents.items.products.some(function (product) {
        return product.name === productName;
    });
}

function validateProductName() {
    var productName = $('#productSearch').find('option:selected').text();

    if (!productName) {
        $('#productSearchError').text('Por favor, selecciona un producto');
        $('#productSearch').addClass('is-invalid');
        return false;
    } else {
        $('#productSearchError').text('');
        $('#productSearch').removeClass('is-invalid');
    }

    return true;
}


function validateProductPrice() {
    var productPrice = $('#productPrice').val();

    // Check if productPrice is not empty
    if (!productPrice) {
        $('#productPriceError').text('El precio del producto no está definido');
        $('#productPrice').addClass('is-invalid');
        return false;
    } else {
        $('#productPriceError').text('');
        $('#productPrice').removeClass('is-invalid');
    }

    var parsedProductPrice = parseFloat(productPrice);
    if (isNaN(parsedProductPrice)) {
        $('#productPriceError').text('Precio del producto inválido debe ser un número');
        $('#productPrice').addClass('is-invalid');
        return false;
    } else if (parsedProductPrice <= 0) {
        $('#productPriceError').text('El precio del producto debe ser mayor que 0');
        $('#productPrice').addClass('is-invalid');
        return false;
    } else {
        $('#productPriceError').text('');
        $('#productPrice').removeClass('is-invalid');
    }

    return true;
}




function validateProductQuantity() {
    var productQuantity = $('#productQuantity').val();

    // Check if productQuantity is not empty
    if (!productQuantity) {
        $('#productQuantityError').text('La cantidad del producto no está definida');
        $('#productQuantity').addClass('is-invalid');
        return false;
    } else {
        $('#productQuantityError').text('');
        $('#productQuantity').removeClass('is-invalid');
    }

    var parsedProductQuantity = parseFloat(productQuantity);
    if (isNaN(parsedProductQuantity) || parsedProductQuantity <= 0) {
        $('#productQuantityError').text('La cantidad del producto debe ser un número mayor que 0');
        $('#productQuantity').addClass('is-invalid');
        return false;
    } else {
        $('#productQuantityError').text('');
        $('#productQuantity').removeClass('is-invalid');
    }

    return true;
}


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