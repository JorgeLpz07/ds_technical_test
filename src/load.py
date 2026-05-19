import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
import pandas as pd
import json
from src.utils import obtener_logger

logger = obtener_logger(__name__)


def obtener_configuracion_tablas() -> dict:
    """
    Escanea la carpeta de esquemas JSON y genera la configuración
    de las tablas de forma 100% dinámica en tiempo de ejecución.
    """
    config = {}
    schemas_dir = Path(__file__).resolve().parent.parent / "schemas"
    
    for schema_file in schemas_dir.glob("*.json"):
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)
            table_name = schema["table_name"]
            config[table_name] = {
                "tipo": schema.get("table_type", "hechos"),
                "pk": schema.get("primary_key", None)
            }
    return config

TABLAS_CONFIG = obtener_configuracion_tablas()

def obtener_conexion_db():
    return psycopg2.connect(
        host="localhost",
        user="apps",
        password="apps",
        port="5432",
        database="test"
    )

def inicializar_db():
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "create_tables.sql"
    if not sql_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo {sql_path}")

    with open(sql_path, "r", encoding="utf-8") as f:
        ddl_sql = f.read()

    conn = obtener_conexion_db()
    try:
        with conn.cursor() as cursor:
            logger.info("Creando tablas e inicializando esquema...")
            cursor.execute(ddl_sql)
        conn.commit()
        logger.info("Tablas creadas/verificadas en la base de datos.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al inicializar tablas: {e}")
        raise e
    finally:
        conn.close()

def limpiar_staging():
    """
    Limpia dinámicamente las tablas de staging asociadas a nuestro modelo.
    """
    conn = obtener_conexion_db()
    try:
        with conn.cursor() as cursor:
            logger.info("Limpiando tablas de staging...")
            for tabla in TABLAS_CONFIG.keys():
                cursor.execute(f"TRUNCATE TABLE stg_{tabla} CASCADE;")
        conn.commit()
        logger.info("Tablas de staging limpiadas exitosamente.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al limpiar tablas de staging: {e}")
        raise e
    finally:
        conn.close()

def cargar_chunk_db(df: pd.DataFrame, table_name: str):
    """
    Inserta de manera 100% genérica cualquier bloque de datos
    directamente en su tabla de staging correspondiente (stg_<nombre_tabla>).
    """
    if df.empty:
        return
        
    if table_name not in TABLAS_CONFIG:
        raise ValueError(f"La tabla '{table_name}' no está definida en la configuración del cargador.")

    target_table = f"stg_{table_name}"
    columnas = list(df.columns)
    columnas_str = ", ".join(columnas)
    
    query = f"INSERT INTO {target_table} ({columnas_str}) VALUES %s;"
    
    # Conversión segura a tipos de datos nativos
    df_limpio = df.astype(object).where(pd.notnull(df), None)
    valores = [tuple(row) for row in df_limpio.to_numpy()]
    
    conn = obtener_conexion_db()
    try:
        with conn.cursor() as cur:
            execute_values(cur, query, valores)
            conn.commit()
            logger.info(f"  -> {len(valores)} registros cargados en staging de '{table_name}'.")
    except Exception as e:
        conn.rollback()
        logger.error(f"  -> Fallo la insercion en '{target_table}': {e}")
        raise e
    finally:
        conn.close()


