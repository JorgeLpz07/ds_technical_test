create or replace function fn_calcular_inventario_diario()
returns void
language plpgsql
as $$
begin
    drop table if exists gold_inventario_diario cascade;

    create table gold_inventario_diario as
    with movimientos_diarios as (
        -- Agrupar entradas y salidas por día
        select m.fecha, m.almacen_id, m.articulo_id 
            , sum(case when m.tipo_movto = 'E' then unidades else 0 end) as entradas_diarias
            , sum(case when m.tipo_movto = 'S' then unidades else 0 end) as salidas_diarias
        from movimientos m 
        group by m.fecha, m.almacen_id, m.articulo_id
    ),
    saldos_acumulados as (
        -- Calculamos inventario final
        select fecha, almacen_id, articulo_id, entradas_diarias, salidas_diarias
        , sum(entradas_diarias - salidas_diarias) over(partition by almacen_id, articulo_id order by fecha asc) as unidades_fin
        from movimientos_diarios 
    )
    select a.fecha, a.almacen_id, a.articulo_id
        , a.unidades_inicio, a.entradas_diarias, a.salidas_diarias, a.unidades_fin
        , coalesce(a.unidades_inicio * a.costo_unitario, 0) as costo_total_inicio
        , coalesce(a.entradas_diarias * a.costo_unitario, 0) as entradas_costos
        , coalesce(a.salidas_diarias * a.costo_unitario, 0) as salidas_costos
        , coalesce(a.unidades_fin * a.costo_unitario, 0) as costo_total_fin
    from(
        select s.fecha, s.almacen_id, s.articulo_id 
            , coalesce(s.unidades_fin - (s.entradas_diarias - s.salidas_diarias),0) as unidades_inicio
            , s.entradas_diarias, s.salidas_diarias , s.unidades_fin 
            , coalesce(c.costo_unitario, 0) as costo_unitario
        from saldos_acumulados s
        inner join gold_dim_articulo_costo c on c.articulo_id = s.articulo_id 
        )a;

    -- Agregamos la llave primaria para optimizar consultas en la base de datos
    alter table gold_inventario_diario add primary key (fecha, almacen_id, articulo_id);
end;
$$;