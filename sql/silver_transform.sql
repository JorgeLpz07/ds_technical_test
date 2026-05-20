-- ==========================================
-- CAPA SILVER: LIMPIEZA Y DEDUPLICACIÓN
-- ==========================================

-- ---------------------------------------------------------
-- 1. CATÁLOGOS (Dimensiones) - Estrategia: UPSERT
-- ---------------------------------------------------------

-- Almacenes
INSERT INTO almacenes (almacen_id, nombre)
SELECT DISTINCT 
    almacen_id, 
    TRIM(nombre) AS nombre 
FROM stg_almacenes
WHERE almacen_id IS NOT NULL
ON CONFLICT (almacen_id) DO UPDATE 
SET nombre = EXCLUDED.nombre;

-- Artículos
INSERT INTO articulos (articulo_id, sku, nombre)
SELECT DISTINCT 
    articulo_id, 
    TRIM(sku) AS sku, 
    TRIM(nombre) AS nombre 
FROM stg_articulos
WHERE articulo_id IS NOT NULL
ON CONFLICT (articulo_id) DO UPDATE 
SET 
    sku = EXCLUDED.sku,
    nombre = EXCLUDED.nombre;


-- ---------------------------------------------------------
-- 2. TABLAS DE HECHOS - Estrategia: DELETE-INSERT (Idempotencia)
-- ---------------------------------------------------------

-- Movimientos
-- A) Borrar fechas a reprocesar para garantizar idempotencia
DELETE FROM movimientos 
WHERE fecha IN (SELECT DISTINCT fecha FROM stg_movimientos WHERE fecha IS NOT NULL);

-- B) Insertar datos deduplicados asegurando integridad referencial
INSERT INTO movimientos (fecha, almacen_id, tipo_movto, articulo_id, unidades, costo_unitario, costo_total)
SELECT DISTINCT 
    m.fecha, 
    m.almacen_id, 
    m.tipo_movto, 
    m.articulo_id, 
    m.unidades, 
    m.costo_unitario, 
    m.costo_total
FROM stg_movimientos m
INNER JOIN almacenes al ON m.almacen_id = al.almacen_id
INNER JOIN articulos ar ON m.articulo_id = ar.articulo_id
WHERE m.fecha IS NOT NULL;


-- Ventas
-- A) Borrar fechas a reprocesar para garantizar idempotencia
DELETE FROM ventas 
WHERE fecha IN (SELECT DISTINCT fecha FROM stg_ventas WHERE fecha IS NOT NULL);

-- B) Insertar datos deduplicados asegurando integridad referencial
INSERT INTO ventas (fecha, almacen_id, articulo_id, unidades, precio_unitario, precio_total)
SELECT DISTINCT 
    v.fecha, 
    v.almacen_id, 
    v.articulo_id, 
    v.unidades, 
    v.precio_unitario, 
    v.precio_total
FROM stg_ventas v
INNER JOIN almacenes al ON v.almacen_id = al.almacen_id
INNER JOIN articulos ar ON v.articulo_id = ar.articulo_id
WHERE v.fecha IS NOT NULL;
