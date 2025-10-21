# 1. name()   nombre ramdom
# 2. email()  email inventado
# 3. phone_number() numero de telefono
# 4. address() dirección
# 5. date_time_this_year()  generador de fecha
# 6. city()  Ciudad aleatoria
# 7. random_int()    numero entero aleatorio
# 8. coordinate()    coordenadas en el mapa
# 9. sentence()     frase de relleno
# 10. pydecimal()   para generar numeros decimales

import mysql.connector
import psycopg2
from faker import Faker
import random
from datetime import datetime

fake = Faker('es_ES')
NUM_REGISTROS_BASE = 15 

DB_CREDS = {
    "host": "localhost",
    "user": "user",
    "password": "user123",
    "database": "negocio"
}

DB_CONFIGS = {
    "PostgreSQL": {"port": 5432, "driver": "psycopg2"},
    "MySQL":      {"port": 3306, "driver": "mysql"}, 
    "MariaDB":    {"port": 3308, "driver": "mysql"},
}


def get_db_connection(config):
    """Establece la conexión a la base de datos."""
    if config["driver"] == "psycopg2":
        return psycopg2.connect(**DB_CREDS, port=config["port"])
    else:
        return mysql.connector.connect(**DB_CREDS, port=config["port"])

def fetch_ids(cursor, table):
    """Obtiene todos los IDs de una tabla. Crucial para FKs."""
    try:
        cursor.execute(f"SELECT id FROM {table}")
        return [row[0] for row in cursor.fetchall()]
    except Exception:
        return []

# --- FUNCIONES DE INSERCIÓN LÓGICA POR TABLA (ORDENADO POR DEPENDENCIAS) ---

def insert_usuario_zona(cursor, conn):
    """Inserta datos en tablas raíz: Usuario y Zona."""
    
    # 1 Tabla Usuario
    sql_user = "INSERT INTO Usuario (nombre, correo, telefono, direccion, fechaDeRegistro) VALUES (%s, %s, %s, %s, %s)"
    data_users = [(fake.name(), fake.email(), fake.phone_number(), fake.address(), fake.date_time_this_year()) for _ in range(NUM_REGISTROS_BASE * 2)]
    cursor.executemany(sql_user, data_users)
    print("    - Usuarios insertados.")

    # 2 Tabla Zona 
    sql_zona = "INSERT INTO Zona (nombre, categoria, coordenadas, numeroIncidencias) VALUES (%s, %s, %s, %s)"
    categorias = ['Zona Céntrica', 'Barrio Residencial', 'Área Industrial', 'Zona de Conflicto']
    data_zonas = [(fake.city(), random.choice(categorias), fake.coordinate(), fake.random_int(0, 100)) for _ in range(NUM_REGISTROS_BASE)]
    cursor.executemany(sql_zona, data_zonas)
    print("    - Zonas insertadas.")
    
    conn.commit()


def insert_reporte_sensor(cursor, conn, usuario_ids, zona_ids):
    """Inserta Reporte (depende de Usuario, Zona) y Sensor (depende de Zona)."""
    
    # 3 Tabla Reporte
    sql_reporte = "INSERT INTO Reporte (id_usuario, id_zona, tipoIncidencia, descripcion, fechaHora, estado, prioridad, medioReporte) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    incidentes = ['Robo con violencia', 'Conflicto vecinal', 'Vandalismo', 'Sospecha de actividad']
    estados = ['Nuevo', 'En análisis', 'Escalado a policía', 'Cerrado']
    prioridades = ['Crítica', 'Alta', 'Media', 'Baja']
    medios = ['App Ciudadana', 'Web Oficial', 'Red Social']
    
    data_reportes = []
    for _ in range(NUM_REGISTROS_BASE * 3):
        tipo_incidente = fake.random_element(elements=incidentes)
        descripcion = f"Reporte de {tipo_incidente} cerca de {fake.city()}. Detalle: {fake.paragraph(nb_sentences=2)}"
        
        data_reportes.append((
            random.choice(usuario_ids), random.choice(zona_ids), tipo_incidente, descripcion, 
            fake.date_time_this_year(), fake.random_element(elements=estados), 
            fake.random_element(elements=prioridades), fake.random_element(elements=medios)
        ))
    cursor.executemany(sql_reporte, data_reportes)
    print("    - Reportes insertados.")

    # 4 Tabla Sensor
    sql_sensor = "INSERT INTO Sensor (id_zona, tipo, modelo, estado, fechaInstalacion) VALUES (%s, %s, %s, %s, %s)"
    tipos_sensor = ['Ruido Ambiental', 'Flujo Peatonal', 'Calidad Aire', 'Cámara CCTV']
    
    data_sensores = []
    for _ in range(NUM_REGISTROS_BASE):
        modelo_str = f"MOD-{fake.random_int(min=100, max=999)}"

        data_sensores.append((
            random.choice(zona_ids), 
            random.choice(tipos_sensor), 
            modelo_str,
            'Activo', 
            fake.date_time_this_year().date()
        ))
    cursor.executemany(sql_sensor, data_sensores)
    print("    - Sensores insertados.")
    
    conn.commit()


def insert_registro_comentario_multimedia_alerta(cursor, conn, usuario_ids, reporte_ids, sensor_ids):
    """Inserta tablas que dependen de Reporte o Sensor."""

    # 5 Tabla RegistroSensor
    sql_registro = "INSERT INTO RegistroSensor (id_sensor, valor, unidad) VALUES (%s, %s, %s)"
    data_registros = [(random.choice(sensor_ids), fake.pydecimal(3, 2, 40, 95), 'dB' if random.random() > 0.5 else 'PPM') for _ in range(NUM_REGISTROS_BASE * 4)]
    cursor.executemany(sql_registro, data_registros)
    print("    - Registros de Sensor insertados.")
    
    # 6 Tabla Comentario
    sql_comentario = "INSERT INTO Comentario (id_usuario, id_reporte, texto) VALUES (%s, %s, %s)"
    data_comentarios = [(random.choice(usuario_ids), random.choice(reporte_ids), fake.sentence(nb_words=8)) for _ in range(NUM_REGISTROS_BASE * 2)]
    cursor.executemany(sql_comentario, data_comentarios)
    print("    - Comentarios insertados.")
    
    # 7 Tabla Multimedia
    sql_multimedia = "INSERT INTO Multimedia (id_reporte, tipoArchivo, rutaArchivo) VALUES (%s, %s, %s)"
    tipos_archivo = ['imagen/jpeg', 'video/mp4']
    data_multimedia = [(random.choice(reporte_ids), fake.random_element(elements=tipos_archivo), f"/evidencia/{fake.uuid4()}") for _ in range(NUM_REGISTROS_BASE)]
    cursor.executemany(sql_multimedia, data_multimedia)
    print("    - Multimedia insertada.")

    # 8 Tabla Alerta
    sql_alerta = "INSERT INTO Alerta (id_reporte, tipo, mensaje) VALUES (%s, %s, %s)"
    tipos_alerta = ['Umbral de Ruido Superado', 'Patrón de Concurrencia Anormal', 'Alerta de Vandalismo']
    data_alertas = [(random.choice(reporte_ids), random.choice(tipos_alerta), fake.sentence(nb_words=10)) for _ in range(NUM_REGISTROS_BASE)]
    cursor.executemany(sql_alerta, data_alertas)
    print("    - Alertas insertadas.")

    conn.commit()


def insert_indicador_informe(cursor, conn, zona_ids, registro_ids):
    """Inserta Indicador (Análisis) y Informe (Decisiones)."""
    
    # 9 Tabla Indicador
    sql_indicador = "INSERT INTO Indicador (id_zona, id_registro_sensor, nombre, valor, descripcion) VALUES (%s, %s, %s, %s, %s)"
    
    cursor.execute("SELECT R.id, S.id_zona FROM RegistroSensor R INNER JOIN Sensor S ON R.id_sensor = S.id")
    registro_data = cursor.fetchall()
    
    nombres_indicador = ['Nivel de Percepción de Riesgo', 'Índice de Conflictos', 'Frecuencia de Incidentes']
    data_indicadores = [(reg[1], reg[0], random.choice(nombres_indicador), fake.pydecimal(2, 2, 1, 10), fake.sentence(nb_words=5)) for reg in registro_data]
    cursor.executemany(sql_indicador, data_indicadores)
    conn.commit()
    print("    - Indicadores insertados.")
    
    # 10 Tabla Informe
    indicador_ids = fetch_ids(cursor, 'Indicador')
    sql_informe = "INSERT INTO Informe (id_indicador, titulo, descripcion, tipo, fuentes) VALUES (%s, %s, %s, %s, %s)"
    tipos_informe = ['Análisis de Riesgo', 'Recomendaciones Operativas', 'Resumen Mensual de Seguridad']
    
    data_informes = []
    for i_id in indicador_ids:
        titulo = fake.random_element(elements=tipos_informe) + f" - {fake.city()}"
        data_informes.append((random.choice(indicador_ids), titulo, fake.text(max_nb_chars=200), fake.random_element(elements=tipos_informe), "Sensores, Reportes, Datos Públicos"))
    cursor.executemany(sql_informe, data_informes)
    print("    - Informes insertados.")
    
    conn.commit()


# --- FUNCIÓN PRINCIPAL DE EJECUCIÓN ---

def main():
    """Conecta a cada DB y ejecuta las inserciones de forma lógica."""
    print("--- INICIO DEL PROCESO DE RELLENO DE BASES DE DATOS (LÓGICA DE NEGOCIO) ---")
    
    for db_name, config in DB_CONFIGS.items():
        conn = None
        try:
            print(f"\n--- Conectando a {db_name} en puerto {config['port']} ---")
            conn = get_db_connection(config)
            cursor = conn.cursor()

            # 1. Insertar entidades raíz y obtener IDs
            insert_usuario_zona(cursor, conn)
            usuario_ids = fetch_ids(cursor, 'Usuario')
            zona_ids = fetch_ids(cursor, 'Zona')

            # 2. Insertar entidades dependientes de nivel 1
            insert_reporte_sensor(cursor, conn, usuario_ids, zona_ids)
            reporte_ids = fetch_ids(cursor, 'Reporte')
            sensor_ids = fetch_ids(cursor, 'Sensor')

            # 3. Insertar entidades dependientes de nivel 2
            insert_registro_comentario_multimedia_alerta(cursor, conn, usuario_ids, reporte_ids, sensor_ids)
            registro_ids = fetch_ids(cursor, 'RegistroSensor')

            # 4. Insertar entidades de análisis final (mondongo)
            insert_indicador_informe(cursor, conn, zona_ids, registro_ids)
            
            conn.close()
            print(f"Relleno de {db_name} completado y conexión cerrada.")
            
        except Exception as e:
            print(f"ERROR CRÍTICO al conectar o rellenar {db_name} (Puerto {config['port']}):")
            print(f"Asegúrate de que el contenedor de {db_name} esté corriendo en el puerto {config['port']} y que la base de datos esté inicializada.")
            print(f"Detalle del error: {e}")
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    main()