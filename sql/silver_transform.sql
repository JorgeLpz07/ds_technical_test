-- ==========================================
-- CAPA SILVER: LIMPIEZA Y DEDUPLICACIÓN
-- ==========================================

-- ---------------------------------------------------------
-- 1. CATÁLOGOS (Dimensiones) - Estrategia: UPSERT
-- ---------------------------------------------------------

-- Almacenes
INSERT INTO almacenes (almacen_id, nombre)
SELECT DISTINCT 
    TRIM(almacen_id) AS almacen_id, 
    TRIM(nombre) AS nombre 
FROM stg_almacenes
WHERE almacen_id IS NOT NULL
ON CONFLICT (almacen_id) DO UPDATE 
SET nombre = EXCLUDED.nombre;

-- Artículos
INSERT INTO articulos (articulo_id, sku, nombre)
SELECT DISTINCT 
    TRIM(articulo_id) AS articulo_id, 
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
    TRIM(m.almacen_id), 
    TRIM(m.tipo_movto), 
    TRIM(m.articulo_id), 
    m.unidades, 
    m.costo_unitario, 
    m.costo_total
FROM stg_movimientos m
INNER JOIN almacenes al ON TRIM(m.almacen_id) = al.almacen_id
INNER JOIN articulos ar ON TRIM(m.articulo_id) = ar.articulo_id
WHERE m.fecha IS NOT NULL;


-- Ventas
-- A) Borrar fechas a reprocesar para garantizar idempotencia
DELETE FROM ventas 
WHERE fecha IN (SELECT DISTINCT fecha FROM stg_ventas WHERE fecha IS NOT NULL);

-- B) Insertar datos deduplicados asegurando integridad referencial
INSERT INTO ventas (fecha, almacen_id, articulo_id, unidades, precio_unitario, precio_total)
SELECT DISTINCT 
    v.fecha, 
    TRIM(v.almacen_id), 
    TRIM(v.articulo_id), 
    v.unidades, 
    v.precio_unitario, 
    v.precio_total
FROM stg_ventas v
INNER JOIN almacenes al ON TRIM(v.almacen_id) = al.almacen_id
INNER JOIN articulos ar ON TRIM(v.articulo_id) = ar.articulo_id
WHERE v.fecha IS NOT NULL;
