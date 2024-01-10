# inventario


// EXPORTAR UNA BASE DE DATOS
python manage.py dumpdata --indent 2 > database.json

// RESTAURAR UNA BASE DE DATOS
python manage.py loaddata database.json

