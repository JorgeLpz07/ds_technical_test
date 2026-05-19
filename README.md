# Pipeline de Datos (ETL) - Prueba Técnica

Este proyecto implementa un pipeline robusto y escalable de Extracción, Transformación y Carga (ETL) desarrollado en Python y PostgreSQL para procesar y consolidar información de almacenes, artículos, movimientos y ventas.

---

## Arquitectura y Decisiones de Diseño

Durante el desarrollo de esta solución se tomaron decisiones clave para asegurar que el pipeline sea eficiente, robusto y de grado de producción:

### 1. Desacoplamiento de Ingesta (Staging) y Consolidación
*   **Enfoque**: Se decidió separar completamente el proceso de **ingesta y transformación inicial (ETL)** de la **consolidación final en producción (ELT)**.
*   **Razón**: Evitar tiempo de inactividad (downtime) y el uso de operaciones destructivas (`TRUNCATE CASCADE`) en tablas de producción finales dentro del código de ingesta. 
*   **Resultado**: El pipeline principal limpia y carga la información incremental en las tablas de staging (`stg_*`). La deduplicación y la inserción a las tablas finales de producción se delega a procesos de base de datos independientes downstream (ej. dbt, procedimientos almacenados o herramientas de orquestación SQL).

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
*   **Enfoque**: Las tablas de staging son truncadas únicamente **una vez al inicio de todo el pipeline**.
*   **Resultado**: Los bloques individuales correspondientes a la misma tabla se insertan secuencialmente (append) acumulándose en staging de forma limpia y garantizando que no se dupliquen registros de ejecuciones previas incompletas.

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
   Configura las credenciales de conexión en tu base de datos o utiliza los valores predeterminados de PostgreSQL local.

3. **Ejecutar el Pipeline**:
   ```bash
   python main.py
   ```

4. **Monitoreo (Logs)**:
   La ejecución escribe logs detallados en consola y de forma persistente rotando diariamente en la carpeta `logs/etl.log`.
