import sys
from src.utils import configurar_logging, obtener_logger
from src.extract import extraer_csv
from src.transform import transformar_chunk
from src.load import (
    TABLAS_CONFIG, 
    inicializar_db, 
    limpiar_staging, 
    cargar_chunk_db
)
from pathlib import Path
from src.load import obtener_conexion_db

# Inicializamos y obtenemos el logger para el script principal
configurar_logging()
logger = obtener_logger(__name__)

def ejecutar_etl():
    """
    Orquestador principal del proceso ETL/ELT.
    """
    logger.info("==================================================")
    logger.info("INICIANDO PIPELINE DE DATOS (ETL/ELT)")
    logger.info("==================================================")
    
    try:
        # Paso 1: Crear tablas fisicas si no existen
        inicializar_db()
        
        # Paso 2: Limpiar tablas staging de cargas previas
        limpiar_staging()
        
        # Paso 3: Extraer, transformar e insertar chunks a Staging
        for table_name in TABLAS_CONFIG.keys():
            logger.info(f"Iniciando procesamiento de tabla: {table_name}")
            
            # chunksize=100 para optimizacion de memoria
            generador_chunks = extraer_csv(table_name, chunksize=500)
            
            for i, chunk_df in enumerate(generador_chunks):
                logger.info(f"  -> Procesando bloque (chunk) {i} con {len(chunk_df)} registros...")
                
                # Transformar (renombrar columnas, limpieza de nulos/espacios)
                chunk_limpio = transformar_chunk(chunk_df, table_name)
                
                # Cargar a base de datos en tabla staging
                cargar_chunk_db(chunk_limpio, table_name)

        logger.info("==================================================")
        logger.info("Iniciando ejecuciones SQL (Capa Silver y Gold)...")
        
        # Leemos los archivos SQL
        sql_silver_path = Path(__file__).resolve().parent / "sql" / "silver_transform.sql"
        sql_gold_path = Path(__file__).resolve().parent / "sql" / "gold_precios_costos.sql"
        sql_inventario_path = Path(__file__).resolve().parent / "sql" / "sp_inventario_diario.sql"
        sql_ventas_margen_path = Path(__file__).resolve().parent / "sql" / "sp_ventas_margen.sql"
        sql_indicadores_path = Path(__file__).resolve().parent / "sql" / "sp_indicadores_negocio.sql"
        
        with open(sql_silver_path, "r", encoding="utf-8") as f:
            sql_silver_script = f.read()
            
        with open(sql_gold_path, "r", encoding="utf-8") as f:
            sql_gold_script = f.read()

        with open(sql_inventario_path, "r", encoding="utf-8") as f:
            sql_inventario_script = f.read()
            
        with open(sql_ventas_margen_path, "r", encoding="utf-8") as f:
            sql_ventas_margen_script = f.read()
            
        with open(sql_indicadores_path, "r", encoding="utf-8") as f:
            sql_indicadores_script = f.read()

        # Abrimos UNA sola conexión para todo el bloque
        conn = obtener_conexion_db()
        try:
            with conn.cursor() as cursor:
                logger.info(" -> Ejecutando Capa Silver (Deduplicación y Limpieza)...")
                cursor.execute(sql_silver_script)
                
                logger.info(" -> Ejecutando Capa Gold (Catálogos de Costos y Precios)...")
                cursor.execute(sql_gold_script)
                
                logger.info(" -> Creando Funciones de Negocio (Postgres 9.6)...")
                cursor.execute(sql_inventario_script)
                cursor.execute(sql_ventas_margen_script)
                cursor.execute(sql_indicadores_script)
                
                logger.info(" -> Ejecutando Cálculo de Inventario Diario...")
                cursor.execute("SELECT fn_calcular_inventario_diario();")
                
                logger.info(" -> Ejecutando Cálculo de Ventas y Margen...")
                cursor.execute("SELECT fn_calcular_ventas_margen();")
                
                logger.info(" -> Ejecutando Consolidación de Indicadores de Negocio...")
                cursor.execute("SELECT fn_calcular_indicadores_negocio();")
                
            conn.commit()
            logger.info("Capas Silver y Gold y KPIs de Negocio creados con éxito.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error durante las ejecuciones SQL: {e}")
        finally:
            conn.close()

        logger.info("==================================================")
        logger.info("PIPELINE ETL FINALIZADO CON EXITO")
        logger.info("==================================================")

    except Exception as e:
        logger.error(f"[ERROR CRITICO] El pipeline fallo: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_etl()
