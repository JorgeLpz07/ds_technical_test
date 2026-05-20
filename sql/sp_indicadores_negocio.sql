create or replace function fn_calcular_indicadores_negocio()
returns void
language plpgsql
as $$
begin
    drop table if exists gold_indicadores_negocio cascade;

    create table gold_indicadores_negocio as
    with base_indicadores as (
        -- Unir tablas maestras y asegurar ceros en valores nulos
        select 
            coalesce(i.fecha, v.fecha) as fecha,
            coalesce(i.almacen_id, v.almacen_id) as almacen_id,
            coalesce(i.articulo_id, v.articulo_id) as articulo_id,
            coalesce(i.unidades_inicio, 0) as unidades_inicio,
            coalesce(i.entradas_diarias, 0) as entradas_diarias,
            coalesce(i.unidades_fin, 0) as inventario_final,
            coalesce(i.costo_total_fin, 0) as costo_inventario_final,
            coalesce(v.venta_diaria, 0) as venta_diaria,
            coalesce(v.costo_total_venta, 0) as costo_venta_diaria,
            coalesce(v.precio_unitario_venta, 0) as precio_unitario,
            coalesce(v.precio_total_venta, 0) as precio_total
        from gold_inventario_diario i
        full outer join gold_ventas_margen v 
            on i.fecha = v.fecha 
            and i.almacen_id = v.almacen_id 
            and i.articulo_id = v.articulo_id
    ),
    calculos_intermedios as (
        select *,
            (precio_total - costo_venta_diaria) as utilidad
        from base_indicadores
    )
    select 
        c.fecha, c.almacen_id, c.articulo_id, c.inventario_final,
        c.costo_inventario_final, c.venta_diaria, c.costo_venta_diaria,
        c.precio_unitario, c.precio_total, c.utilidad
        ,case 
            when c.precio_total > 0 
            then round((c.utilidad / c.precio_total)::numeric, 4)
            else 0 
        end as margen_bruto
        ,case 
            when (c.unidades_inicio + c.entradas_diarias) > 0 
            then round((c.venta_diaria::numeric / (c.unidades_inicio + c.entradas_diarias)), 4)
            else 0 
        end as sell_through
    from calculos_intermedios c;

    -- Agregamos la llave primaria para optimizar consultas en la base de datos
    alter table gold_indicadores_negocio add primary key (fecha, almacen_id, articulo_id);
end;
$$;