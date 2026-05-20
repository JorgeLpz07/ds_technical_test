# Pipeline de Datos (ETL) - Prueba Técnica

Este proyecto implementa un pipeline robusto y escalable de Extracción, Transformación y Carga (ETL) desarrollado en Python y PostgreSQL para procesar y consolidar información de almacenes, artículos, movimientos y ventas.

---

## Arquitectura y Decisiones de Diseño

Durante el desarrollo de esta solución se tomaron decisiones clave para asegurar que el pipeline sea eficiente, robusto y de grado de producción:

### 1. Desacoplamiento de Ingesta y Consolidación (Patrón Medallion)
*   **Enfoque**: Se implementó una arquitectura ELT utilizando el patrón Medallion.
*   **Capa Bronze (Staging)**: Python extrae la data en bloques (chunks), aplica transformaciones ligeras (*snake_case*, limpieza de espacios y descarte de nulos) mediante Pandas, y deposita la información en PostgreSQL (tablas `stg_*`).
*   **Capa Silver (Producción)**: Mediante el script `silver_transform.sql`, se eliminan los registros duplicados a nivel global y se garantiza la integridad referencial antes de consolidar la información en los catálogos y tablas de hechos finales.

### 2. Procesamiento Eficiente por Bloques (Chunking)
*   **Enfoque**: La lectura de archivos CSV se realiza por bloques (`chunksize=500` o configurable) usando generadores de Pandas.
*   **Razón**: Garantiza que el uso de memoria RAM del pipeline se mantenga constante e independiente del tamaño del archivo de entrada, evitando fallas por memoria insuficiente (`OutOfMemory`) al procesar millones de registros.

### 3. Validación de Calidad e Integridad de Datos Basada en Esquemas
*   **Enfoque**: Toda la estructura de datos se valida declarativamente mediante esquemas en formato JSON (`schemas/*.json`).
*   **Acciones**:
    *   **Estandarización**: Renombrado dinámico de columnas de nombres "raw" (originales en el archivo) a nombres "clean" (estandarizados en BD).
    *   **Limpieza de Texto**: Remoción de espacios en blanco sobrantes (`strip()`) en todas las columnas de tipo texto.
    *   **Filtrado de Nulos**: Identificación automática de registros inválidos que contienen nulos en columnas obligatorias (`required: true`) y descarte preventivo con registro en los logs para auditoría.

### 4. Ciclo de Vida de Tablas Staging
*   **Enfoque**: Las tablas de staging son truncadas **una vez al inicio de todo el pipeline**.
*   **Resultado**: Los bloques individuales correspondientes a la misma tabla se insertan secuencialmente (append) acumulándose en staging de forma limpia y garantizando que no se dupliquen registros de ejecuciones previas incompletas.

### 5. Reprocesamiento Seguro
*   **Enfoque**: Para garantizar que el proceso pueda ejecutarse múltiples veces (al corregir un archivo) sin generar datos duplicados, se implementaron dos estrategias en la capa Silver:
*   Los catálogos (`almacenes`, `articulos`) se actualizan mediante **UPSERT** (`ON CONFLICT DO UPDATE`).
*   Las tablas de hechos (`movimientos`, `ventas`) utilizan el patrón **DELETE-INSERT**, borrando dinámicamente los días a reprocesar antes de insertar la nueva carga. Esto asegura que la información de ese día siempre sea la correcta.

### 6. Particionamiento de Datos
*   **Enfoque**: Al ser este un ejercicio de prueba, se optó por usar tablas estándar para agilizar el desarrollo y las pruebas locales.
*   **Consideración Productiva**: En un entorno real con gran volumen de datos, las tablas de hechos deberían estar particionadas (por ejemplo, por mes). La estrategia exacta dependerá de la versión del motor de base de datos definitivo.

### 7. Seguridad y Configuración
*   **Enfoque**: Las credenciales de conexión fueron desacopladas del código fuente para evitar *hardcoding*. Se requiere un archivo local `.env` en la raíz del proyecto para que el pipeline lea la configuración dinámicamente mediante `python-dotenv`.

> Para efectos practivos se deja el archivo .env en el proyecto para que pueda ser usado directamente sin necesidad de crearlo.
---

## Estructura del Proyecto

```text
├── dags/                  # Orquestación con Airflow (DAGs)
├── data/                  # Archivos CSV fuente
├── notebooks/             # Análisis exploratorio y pruebas rápidas
├── schemas/               # Esquemas JSON de validación por tabla
├── sql/                   # DDL de tablas y procedimientos almacenados de BD
├── src/                   # Código fuente modular
│   ├── config.py          # Configuración de variables de entorno y base de datos
│   ├── extract.py         # Módulo de extracción de archivos CSV
│   ├── load.py            # Módulo para carga a tablas PostgreSQL
│   ├── transform.py       # Módulo para estandarización y calidad de datos
│   └── utils.py           # Funciones de logging y utilidades
├── tests/                 # Pruebas unitarias
├── Dockerfile             # Dockerización de la aplicación
├── docker-compose.yml     # Orquestación de infraestructura de servicios
├── main.py                # Ejecutor principal del Pipeline
└── README.md              # Documentación del proyecto
```

---

## Requisitos Previos

*   Python 3.8 o superior
*   Base de Datos PostgreSQL activa (o desplegada mediante Docker)

---

## Configuración y Ejecución

1. **Instalar Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Variables de Entorno**:
   Crea un archivo `.env` en la raíz del proyecto con las credenciales de tu base de datos (puedes guiarte por las variables requeridas en `src/config.py`).

3. **Ejecutar el Pipeline**:
   ```bash
   python main.py
   ```

4. **Monitoreo (Logs)**:
   La ejecución escribe logs detallados en consola y de forma persistente rotando diariamente en la carpeta `logs/etl.log`.
