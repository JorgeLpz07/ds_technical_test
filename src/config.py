import os
from dotenv import load_dotenv

# Cargamos las variables desde archivo de configuración
load_dotenv()

class Config:
    # Valores de la base de datos
    DDB_HOST = os.getenv('DDB_HOST')
    DDB_USER = os.getenv('DDB_USER')
    DDB_PASSWORD = os.getenv('DDB_PASSWORD')
    DDB_PORT = os.getenv('DDB_PORT')
    DDB_SCHEMA = os.getenv('DDB_SCHEMA')

    # Configuración del batch
    CHUNKSIZE = int(os.getenv('CHUNKSIZE', 500))

    @classmethod
    def get_db_connection_params(cls):
        """Retorna los parámetros de conexión a la base de datos"""
        return {
            'host': cls.DDB_HOST,
            'user': cls.DDB_USER,
            'password': cls.DDB_PASSWORD,
            'port': cls.DDB_PORT,
            'database': cls.DDB_SCHEMA
        }
    
    @classmethod
    def get_chunksize(cls):
        """Retorna el tamaño del batch"""
        return cls.CHUNKSIZE