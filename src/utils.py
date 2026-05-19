import os
import logging
from logging.handlers import RotatingFileHandler

def configurar_logging():
    """
    Configura el sistema de logging para que registre en consola y en archivo.
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "etl.log")
    
    # Formateador detallado
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # Manejador para archivo rotativo (10 MB máximo, mantiene 5 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Manejador para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Limpiar manejadores existentes para evitar duplicación de logs
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def obtener_logger(nombre: str) -> logging.Logger:
    """
    Retorna un logger configurado con el nombre del módulo.
    """
    return logging.getLogger(nombre)
