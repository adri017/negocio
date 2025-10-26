import mysql.connector
import psycopg2
import json
from datetime import datetime

# --- CONFIGURACIÓN DE CONEXIÓN ---
DB_CREDS = {
    "host": "localhost",
    "user": "user",
    "password": "user123",
    "database": "negocio"
}

DB_CONFIGS = {
    "PostgreSQL": {"port": 5432, "driver": "psycopg2"},
    "MySQL":      {"port": 3306, "driver": "mysql"}, # Asumiendo 3306 como puerto principal de MySQL
    "MariaDB":    {"port": 3308, "driver": "mysql"},
}

# --- FUNCIONES DE CONEXIÓN ---

def get_db_connection(config):
    """Establece la conexión a la base de datos."""
    if config["driver"] == "psycopg2":
        return psycopg2.connect(**DB_CREDS, port=config["port"])
    else:
        # Usa mysql-connector para MySQL y MariaDB
        return mysql.connector.connect(**DB_CREDS, port=config["port"])

# --- FUNCIONES DE EXTRACCIÓN Y ANÁLISIS ---

def analizar_postgresql(conn):
    """
    Métrica: Zonas de Alto Riesgo por Incidencia y Prioridad.
    Obtiene las 5 zonas con más reportes de prioridad 'Crítica' o 'Alta'.
    """
    print("-> Extrayendo Zonas de Alto Riesgo (PostgreSQL)...")
    
    # Consulta que une Zona y Reporte, agrupando por Zona y contando reportes críticos/altos.
    sql = """
    SELECT
        Z.nombre AS nombre_zona,
        COUNT(R.id) AS total_incidentes_criticos,
        Z.coordenadas
    FROM Zona Z
    JOIN Reporte R ON Z.id = R.id_zona
    WHERE R.prioridad IN ('Crítica', 'Alta')
    GROUP BY Z.id, Z.nombre, Z.coordenadas
    ORDER BY total_incidentes_criticos DESC
    LIMIT 5;
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    
    resultados = []
    for row in cursor.fetchall():
        resultados.append({
            "zona": row[0],
            "incidentes_criticos": row[1],
            "coordenadas": row[2]
        })
    cursor.close()
    
    return {
        "fecha_generacion": datetime.now().isoformat(),
        "descripcion": "Las 5 zonas con mayor cantidad de incidentes reportados con prioridad Crítica o Alta. Usado para la asignación de patrullaje y recursos de emergencia.",
        "top_zonas": resultados
    }

def analizar_mysql(conn):
    """
    Métrica: Eficiencia de Cierre de Reportes por Usuario.
    Obtiene los 5 usuarios con más reportes resueltos y el promedio de comentarios
    que sus reportes reciben, indicando la interacción comunitaria.
    """
    print("-> Extrayendo Eficiencia de Reportes (MySQL)...")
    
    # Consulta que une Usuario, Reporte y Comentario.
    sql = """
    SELECT
        U.nombre AS nombre_usuario,
        COUNT(R.id) AS reportes_resueltos,
        AVG(Sub.total_comentarios) AS promedio_comentarios_por_reporte
    FROM Usuario U
    JOIN Reporte R ON U.id = R.id_usuario
    LEFT JOIN (
        SELECT id_reporte, COUNT(id) AS total_comentarios
        FROM Comentario
        GROUP BY id_reporte
    ) Sub ON R.id = Sub.id_reporte
    WHERE R.estado = 'Cerrado' OR R.estado = 'Resuelto'
    GROUP BY U.id, U.nombre
    ORDER BY reportes_resueltos DESC
    LIMIT 5;
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    
    resultados = []
    for row in cursor.fetchall():
        resultados.append({
            "usuario": row[0],
            "reportes_resueltos": row[1],
            # Formatear el promedio a dos decimales
            "promedio_comentarios": round(float(row[2]) if row[2] else 0.0, 2)
        })
    cursor.close()
    
    return {
        "fecha_generacion": datetime.now().isoformat(),
        "descripcion": "Usuarios con mayor cantidad de reportes resueltos y el promedio de comentarios en esos reportes. Mide la productividad de los usuarios clave y la interacción comunitaria.",
        "top_usuarios_eficientes": resultados
    }

def analizar_mariadb(conn):
    """
    Métrica: Correlación entre Alertas de Sensor y Reportes Ciudadanos.
    Cuenta cuántos reportes ciudadanos existen en una zona y tiempo similar a un registro de sensor,
    validando la correlación entre percepción (Reporte) y tecnología (Sensor).
    """
    print("-> Extrayendo Correlación Sensor-Reporte (MariaDB)...")
    
    # Consulta optimizada para MariaDB:
    # 1. Empieza con RegistroSensor (la fuente de datos de tiempo).
    # 2. Une con Sensor y Zona para obtener la ubicación.
    # 3. Une con Reporte y Alerta usando la condición de la misma Zona.
    # 4. Aplica la condición temporal.
    sql = """
        SELECT
        Z.nombre AS zona,
        S.tipo AS tipo_sensor,
        COUNT(DISTINCT R.id) AS reportes_ciudadanos_cercanos
        FROM RegistroSensor RS
        JOIN Sensor S ON RS.id_sensor = S.id
        JOIN Zona Z ON S.id_zona = Z.id
        JOIN Reporte R ON R.id_zona = Z.id
        JOIN Alerta A ON A.id_reporte = R.id
        WHERE
            -- Corregido: R.fechaHora está entre 2 días antes y la hora del registro del sensor (RS.fecha)
            R.fechaHora BETWEEN DATE_SUB(RS.fecha, INTERVAL 2 DAY) AND RS.fecha
        GROUP BY Z.nombre, S.tipo
        HAVING COUNT(R.id) > 0
        ORDER BY reportes_ciudadanos_cercanos DESC
        LIMIT 5;
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    
    resultados = []
    for row in cursor.fetchall():
        resultados.append({
            "zona": row[0],
            "sensor": row[1],
            "reportes_ciudadanos_afectados": row[2]
        })
    cursor.close()
    
    return {
        "fecha_generacion": datetime.now().isoformat(),
        "descripcion": "Mide el número de reportes ciudadanos en zonas donde la fecha del reporte coincide con la de un registro de sensor ± 1 hora. Esto valida la correlación entre la percepción del ciudadano y los datos tecnológicos.",
        "top_correlaciones_sensor_reporte": resultados
    }

def funcionConjunta():
    sql="""
       SELECT
            Z.nombre AS zona_mas_critica,
            COUNT(R.id) AS reportes_alta_prioridad_total
        FROM Zona Z
        JOIN Reporte R ON Z.id = R.id_zona
        WHERE
            R.prioridad = 'Alta'
        GROUP BY
            Z.nombre
        ORDER BY
            reportes_alta_prioridad_total DESC
        LIMIT 1;
        """
    dbNames = ["PostgreSQL", "MySQL", "MariaDB"]
    resultado = []

    for db in dbNames:
        conn = None
        try:
            config = DB_CONFIGS[db]
            conn = get_db_connection(config)

            cursor = conn.cursor()

            cursor.execute(sql)
        
            for row in cursor.fetchall():
                resultado.append({
                    "zona_mas_critica": row[0],
                    "reportes_alta_prioridad_total": row[1],
                })
            cursor.close()
        except Exception as e:
            print(f"ERROR al procesar {db}:")
            print(f"Detalle: {e}")
        finally:
            if conn:
                conn.close()

    return resultado


    

# --- FUNCIÓN PRINCIPAL ---

def main():
    print("--- INICIO DE EXPORTACIÓN DE ANÁLISIS CLAVE ---")
    
    export_functions = {
        "PostgreSQL": (analizar_postgresql, "analisisZonasRiesgo.json"),
        "MySQL":      (analizar_mysql, "analisis_eficiencia_usuarios.json"),
        "MariaDB":    (analizar_mariadb, "analisisCorrelacionSensor.json"),
    }
    
    for db_name, (analysis_func, filename) in export_functions.items():
        conn = None
        try:
            config = DB_CONFIGS[db_name]
            conn = get_db_connection(config)
            
            # 1. Ejecutar análisis
            data = analysis_func(conn)
            
            # 2. Guardar en JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            print(f"Análisis de {db_name} exportado a {filename}")

        except Exception as e:
            print(f"ERROR al procesar {db_name}:")
            print(f"Detalle: {e}")
        finally:
            if conn:
                conn.close()

    with open("datosDeLasTresBases", 'w' ,encoding='utf-8') as f:
        json.dump(funcionConjunta(),f,ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()