# Examen técnico.

Se te ha compartido las bases de datos necesarias para este examen. Vienen adjuntas en el correo.

Favor de contestar los siguientes puntos:

## 1.- Creación de DB/PYTHON
En este punto me gustaría que generarán un script en python en donde hagas un proceso de ETL.

### 1.1- Proceso de ETL en Python:

* Leer los archivos CSV proporcionados
* Validar integridad básica de los datos
* Eliminar registros duplicados
* Estandarizar nombres de columnas a formato snake_case
* Eliminar espacios adicionales en campos de texto
* Validar tipos de datos
* Documentar errores o inconsistencias detectadas

### 1.2- Una vez ya con la información limpia, escoge un motor de base de datos (de preferencia postgreSQL) para que generes una tabla por cada archivo CSV

## 2.- Creación de tablas de información.

Para este punto, si es necesario pueden buscar las fórmulas de ciertos KPI’s en línea

### 2.1.- Necesito que me generes una tabla de costos unitarios (por artículos).

* Articulo_id
* costo_unitario

### 2.2.- Necesito que me generes una tabla de precios de lista (por artículos).

* Articulo_id
* precio_lista

### 2.3.- Necesito que me formules un SP que me calcule el inventario diario por día. Para calcular el inventario es necesario sumar las entradas y las salidas de la tabla de movimientos. Yo necesito que me generes un SP que genere una tabla (en dado caso que no exista) y me deposite el inventario diario por día (junto con sus costos)

* Fecha (diaria)
* Almacen_id
* Articulo_id
* Unidades_inicio (inventario al inicio del día)
* Entradas_diarias
* Salidas_diarias
* Unidades_fin (inventario al fin del día)
* Costo_total inicio (costo al inicio del día)
* Entradas_costos
* Salidas_costos
* Costos_total_fin (costos al fin del día)

### 2.4.- Necesito que me formules un SP que me calcule las ventas y su margen de utilidad. En dado caso que no exista la tabla, generarla con el SP

* Fecha
* Almacen_id
* Articulo_id
* Venta_diaria
* Costo_unitario_venta
* Costo_total_venta
* Precio_unitario_venta
* Precio_total_venta
* Descuento
* Porcentaje_descuento

### 2.5.- Necesito que me generes un SP que me calcule indicadores de negocios. En caso de que la tabla no exista, generarla con el SP.

* Fecha
* Almacen_id
* Articulo_id
* Inventario_final
* Costo_inventario_final
* Venta_diaria
* Costo_venta_diaria
* Precio_unitario
* Precio_total
* Utilidad
* Margen_bruto
* Sell-through

## 3.- Creación de Monitor

Diseña un dashboard ejecutivo que permita visualizar el desempeño comercial de la empresa. El dashboard deberá incluir al menos:

### 3.1.- KPIs principales

* Venta total
* Margen bruto
* Utilidad
* Sell-through
* Inventario final
* Ticket promedio
* % descuento promedio

### 3.2.- Segmentaciones mínimas

* Fecha
* Almacén
* Artículo

### 3.3.- Visualizaciones sugeridas

* tendencia diaria de ventas
* top artículos
* comparación contra periodo anterior
* evolución de margen

## Entregables Esperados

* Scripts SQL
* Scripts Python
* README con instrucciones
* Explicación técnica breve
* Supuestos realizados
* Looker Studio (o cualquier otro BI en el que se haya decidido hacer el dashboard)

## Bonus (Opcional)

* Docker
* Dbt
* Airflow
* Pruebas automáticas
* Logging
* Manejo eficiente de grandes volúmenes
