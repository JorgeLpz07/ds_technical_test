-- ==========================================
-- Capa Gold
-- Creamos tablas de costo unitario 
--  y precio de lista según el ultimo valor obtenido por fechas.
-- ==========================================

-- Tabla de costo unitario
drop table if exists gold_dim_articulo_costo cascade;

create table gold_dim_articulo_costo as 
select a.articulo_id, a.costo_unitario 
from (
	select m.articulo_id, m.costo_unitario,
		ROW_NUMBER() over(partition by articulo_id order by fecha desc) as rn
	from movimientos m 
	where m.tipo_movto = 'E'
		and m.costo_unitario is not null
)a
where a.rn = 1;

-- Tabla de precio de lista
drop table if exists gold_dim_articulo_precio cascade;

create table gold_dim_articulo_precio as 
select a.articulo_id, a.precio_unitario as precio_lista
from(
	select v.articulo_id, v.precio_unitario, fecha,
		ROW_NUMBER() over(partition by v.articulo_id order by fecha desc) as  rn
	from ventas v 
	where v.precio_unitario is not null
)a
where a.rn = 1;
