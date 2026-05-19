import json
from pathlib import Path
import sys
import pandas as pd
from typing import Generator
from src.utils import obtener_logger

logger = obtener_logger(__name__)


def cargar_esquema(table_name: str) -> dict:
    """
    Carga el esquema para la tabla especificada
    
    Args:
        table_name (str): Nombre de la tabla
        
    Returns:
        dict: Esquema de la tabla
    """

    schema_path = Path(__file__).parent.parent / "schemas" / f"{table_name}.json"

    # Validamos que el archivo de esquema exista
    if not schema_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo de esquema para la tabla {table_name}")

    # Abrimos y leemos el archivo de esquema
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extraer_csv(table_name:str, chunksize:int =100) -> Generator[pd.DataFrame, None, None]:
    """
    Extrae los datos del archivo CSV y los carga a una dataframe de pandas.

    Args:
        table_name (str): Nombres de la tabla
        chunksize (int): Tamaño del bloque de registros.

    Yields:
        pd.DataFrame: Un bloque (chunk) de datos listo para ser transformado.
    """

    # Obtenemos la ruta del archivo
    csv_path = Path(__file__).resolve().parent.parent / "data" / f"{table_name}.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo CSV para la tabla {table_name}")

    # Cargamos el esquema de la tabla
    schema = cargar_esquema(table_name)

    # Mapeamos los tipos de datos obtenidos de esquema
    dtypes = {}
    parse_dates = []

    for col in schema["columns"]:
        raw_name = col["raw_name"]
        if col.get("is_date", False):
            parse_dates.append(raw_name)
        else:
            dtypes[raw_name] = col.get("pandas_type", "object")

    # Leemos el archivo CSV
    logger.info(f"Leyendo archivo CSV para la tabla '{table_name}'")

    chunks_iterators = pd.read_csv(
        csv_path,
        dtype=dtypes,
        parse_dates=parse_dates,
        encoding="utf-8",
        chunksize=chunksize
    ) 
    
    # Iteramos los chunks
    for chunk in chunks_iterators:
        yield chunk

if __name__ == "__main__":
    # Valdiamos parametros
    if len(sys.argv) < 2:
        print("[ERROR] Falta especificar el nombre de la tabla.")
        print("Uso: python extract.py <table_name>")
        sys.exit(1)

    # Obtenemos el nombre de la tabla a leer
    table_name = sys.argv[1].lower()

    try:
        print(f"Iniciando la extraccion por bloques de la tabla {table_name}")
        
        generador_chunks = extraer_csv(table_name, chunksize=200)

        for i, chunk in enumerate(generador_chunks):
            print(f"Procesando chunk {i}")
            print(f"  - Registros en este bloque: {len(chunk)}")
            print(f"  - Columnas detectadas: {list(chunk.columns)}")

        print("\n--- Extraccion finalizada con exito ---")

    except Exception as e:
        print(f"\n[ERROR]: {e}\n")

    
    