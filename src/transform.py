import pandas as pd 
from src.extract import cargar_esquema
import sys
from src.utils import obtener_logger

logger = obtener_logger(__name__)


def estandarizar_columnas(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Renombra las columnas del DataFrame mapeando raw_name a clean_name
    según las definiciones explícitas del esquema JSON.
    """
    schema = cargar_esquema(table_name)
    
    mapa_renombrado = {
        col["raw_name"]: col.get("clean_name", col["raw_name"]) 
        for col in schema["columns"]
    }
    
    return df.rename(columns=mapa_renombrado)

def limpiar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia los espacios adicionales en campos de texto.
    """
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    return df

def validar_integridad(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Valida la integridad de los datos del DataFrame.
    """
    schema = cargar_esquema(table_name)

    for col in schema["columns"]:
        col_name = col.get("clean_name", col["raw_name"])

        # Validamos si la columna es obligatoria
        if col_name in df.columns and col.get("required", False):
            nulos = df[col_name].isna().sum()

            if nulos > 0:
                logger.warning(
                    f"Inconsistencia en tabla '{table_name}': Se detectaron {nulos} "
                    f"valores nulos en la columna obligatoria '{col_name}'. Registros descartados."
                )
                df = df.dropna(subset=[col_name])

    return df

def transformar_chunk(chunk: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Realizamos el proceso de transformación de los chunks de los CSVs. 
    """

    if chunk.empty:
        return chunk

    # Copiamos para evitar errores
    df = chunk.copy()

    # Estandarizamos nombres de las columnas a snake_case
    df = estandarizar_columnas(df, table_name)
    
    # Eliminamos espacios adicionales en campos de texto
    df = limpiar_texto(df)

    # Validar integridad de los datos
    df = validar_integridad(df, table_name)

    return df

if __name__ == "__main__":
    from src.extract import extraer_csv

    if len(sys.argv) < 2:
        print("[ERROR] Falta especificar el nombre de la tabla para probar la transformacion.")
        print("Uso: python src/transform.py <table_name>")
        sys.exit(1)

    table_name = sys.argv[1].lower()

    try:
        print(f"--- Iniciando Prueba de Transformacion para '{table_name}' ---")
        
        # 1. Extraemos el primer bloque (por ejemplo, chunksize=10)
        generador = extraer_csv(table_name, chunksize=10)
        primer_chunk = next(generador)
        
        print("\n[ANTES] Columnas originales:")
        print(list(primer_chunk.columns))
        print("[ANTES] Primeros registros:")
        print(primer_chunk.head(3))
        
        # 2. Transformamos el bloque
        chunk_transformado = transformar_chunk(primer_chunk, table_name)
        
        print("\n[DESPUES] Columnas transformadas:")
        print(list(chunk_transformado.columns))
        print("[DESPUES] Primeros registros limpios:")
        print(chunk_transformado.head(3))
        
        print("\n--- Prueba de Transformacion finalizada con exito ---")

    except Exception as e:
        print(f"\n[ERROR durante la prueba]: {e}\n")
