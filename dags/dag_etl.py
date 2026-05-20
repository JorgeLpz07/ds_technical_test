"""
DAG: dag_etl_pipeline
Descripción: Orquesta el pipeline ELT completo en el orden lógico de dependencias.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Agregamos la raíz al path para permitir la importación del módulo src/
sys.path.insert(0, '/opt/airflow')

from src.utils import configurar_logging, obtener_logger
from src.extract import extraer_csv
from src.transform import transformar_chunk
from src.load import (
    TABLAS_CONFIG,
    inicializar_db,
    limpiar_staging,
    cargar_chunk_db,
)

configurar_logging()
logger = obtener_logger(__name__)

# ID de la conexión configurada dinámicamente vía docker-compose
CONN_ID = 'postgres_default'

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Funciones de Python para la capa Bronze
def task_inicializar_db():
    logger.info("Inicializando esquema de base de datos...")
    inicializar_db()
    logger.info("Esquema inicializado.")

def task_ingesta_bronze():
    logger.info("Iniciando ingesta de archivos CSV a Staging...")
    limpiar_staging()

    for table_name in TABLAS_CONFIG.keys():
        logger.info(f"Procesando tabla: {table_name}")
        for i, chunk_df in enumerate(extraer_csv(table_name, chunksize=500)):
            logger.info(f"  -> Chunk {i}: {len(chunk_df)} registros")
            chunk_limpio = transformar_chunk(chunk_df, table_name)
            cargar_chunk_db(chunk_limpio, table_name)

    logger.info("Ingesta Bronze completada.")


with DAG(
    dag_id='dag_etl_pipeline',
    default_args=default_args,
    description='Pipeline ELT: Bronze -> Silver -> Gold (Inventario, Ventas, KPIs)',
    schedule_interval='0 1 * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    template_searchpath=['/opt/airflow/sql'], # Ruta base para PostgresOperator
    tags=['etl', 'bronze', 'silver', 'gold'],
) as dag:

    # Tareas de Python (Ingesta inicial)
    t1_init = PythonOperator(
        task_id='inicializar_db',
        python_callable=task_inicializar_db,
    )

    t2_bronze = PythonOperator(
        task_id='ingesta_bronze',
        python_callable=task_ingesta_bronze,
    )

    # Tareas SQL (Transformación y Catálogos)
    t3_silver = PostgresOperator(
        task_id='transformar_silver',
        postgres_conn_id=CONN_ID,
        sql='silver_transform.sql',
    )

    t4_gold_catalogos = PostgresOperator(
        task_id='gold_catalogos',
        postgres_conn_id=CONN_ID,
        sql='gold_precios_costos.sql',
    )

    # Registro de Lógica de Negocio
    t5_crear_funciones = PostgresOperator(
        task_id='crear_funciones_kpi',
        postgres_conn_id=CONN_ID,
        sql=[
            'sp_inventario_diario.sql',
            'sp_ventas_margen.sql',
            'sp_indicadores_negocio.sql'
        ],
    )

    # Cálculo de KPIs
    t6_inventario = PostgresOperator(
        task_id='calcular_inventario_diario',
        postgres_conn_id=CONN_ID,
        sql='SELECT fn_calcular_inventario_diario();',
    )

    t7_ventas = PostgresOperator(
        task_id='calcular_ventas_margen',
        postgres_conn_id=CONN_ID,
        sql='SELECT fn_calcular_ventas_margen();',
    )

    t8_indicadores = PostgresOperator(
        task_id='calcular_indicadores_negocio',
        postgres_conn_id=CONN_ID,
        sql='SELECT fn_calcular_indicadores_negocio();',
    )

    # Secuencia de dependencias lógicas
    (
        t1_init
        >> t2_bronze
        >> t3_silver
        >> t4_gold_catalogos
        >> t5_crear_funciones
        >> t6_inventario
        >> t7_ventas
        >> t8_indicadores
    )