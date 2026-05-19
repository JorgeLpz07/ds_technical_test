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
        
        logger.info("==================================================")
        logger.info("PIPELINE ETL FINALIZADO CON EXITO")
        logger.info("==================================================")

    except Exception as e:
        logger.error(f"[ERROR CRITICO] El pipeline fallo: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_etl()
