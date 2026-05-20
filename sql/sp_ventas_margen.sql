create or replace function fn_calcular_ventas_margen()
returns void
language plpgsql
as $$
begin
    drop table if exists gold_ventas_margen cascade;

    create table gold_ventas_margen as
    with ventas_agrupadas as (
        -- Agrupamos ventas diarias y obtenemos costos
        select v.fecha, v.almacen_id, v.articulo_id
            , sum(v.unidades) as venta_diaria
            , c.costo_unitario as costo_unitario_venta
            , (sum(v.unidades) * c.costo_unitario) as costo_total_venta
            , max(v.precio_unitario) as precio_unitario_venta
            , sum(v.precio_total) as precio_total_venta
        from ventas v 
        inner join gold_dim_articulo_costo c on c.articulo_id = v.articulo_id 
        group by v.fecha, v.almacen_id, v.articulo_id, c.costo_unitario
    )
    select a.*,
        greatest(0, (a.precio_unitario_venta * a.venta_diaria) - a.precio_total_venta) as descuento,
        -- Calculamos porcentaje de descuento redondeado a 4 decimales
        case 
            when (a.precio_unitario_venta * a.venta_diaria) > 0 
            then round((greatest(0, (a.precio_unitario_venta * a.venta_diaria) - a.precio_total_venta) 
                    / (a.precio_unitario_venta * a.venta_diaria))::numeric, 4)
            else 0 
        end as porcentaje_descuento
    from ventas_agrupadas a;

    -- Agregamos la llave primaria para optimizar consultas en la base de datos
    alter table gold_ventas_margen add primary key (fecha, almacen_id, articulo_id);
end;
$$;