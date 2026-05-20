-- ==========================================
-- 1. TABLAS FINALES DE PRODUCCIÓN (CON RESTRICCIONES)
-- ==========================================

CREATE TABLE IF NOT EXISTS almacenes (
    almacen_id BIGINT PRIMARY KEY,
    nombre VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS articulos (
    articulo_id BIGINT PRIMARY KEY,
    sku VARCHAR(50),
    nombre VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS movimientos (
    fecha DATE,
    almacen_id BIGINT REFERENCES almacenes(almacen_id),
    tipo_movto VARCHAR(50),
    articulo_id BIGINT REFERENCES articulos(articulo_id),
    unidades INT,
    costo_unitario NUMERIC(12, 2),
    costo_total NUMERIC(12, 2),
    PRIMARY KEY (fecha, almacen_id, tipo_movto, articulo_id, unidades, costo_unitario, costo_total)
);

CREATE TABLE IF NOT EXISTS ventas (
    fecha DATE,
    almacen_id BIGINT REFERENCES almacenes(almacen_id),
    articulo_id BIGINT REFERENCES articulos(articulo_id),
    unidades INT,
    precio_unitario NUMERIC(12, 2),
    precio_total NUMERIC(12, 2),
    PRIMARY KEY (fecha, almacen_id, articulo_id, unidades, precio_unitario, precio_total)
);


-- ==========================================
-- 2. TABLAS DE STAGING (SIN RESTRICCIONES DE UNICIDAD)
-- ==========================================

CREATE TABLE IF NOT EXISTS stg_almacenes (
    almacen_id BIGINT,
    nombre VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS stg_articulos (
    articulo_id BIGINT,
    sku VARCHAR(50),
    nombre VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS stg_movimientos (
    fecha DATE,
    almacen_id BIGINT,
    tipo_movto VARCHAR(50),
    articulo_id BIGINT,
    unidades INT,
    costo_unitario NUMERIC(12, 2),
    costo_total NUMERIC(12, 2)
);

CREATE TABLE IF NOT EXISTS stg_ventas (
    fecha DATE,
    almacen_id BIGINT,
    articulo_id BIGINT,
    unidades INT,
    precio_unitario NUMERIC(12, 2),
    precio_total NUMERIC(12, 2)
);
