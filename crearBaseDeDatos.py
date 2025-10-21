import mysql.connector
import psycopg2

# --- CONFIGURACIÓN DE CONEXIÓN ÚNICA ---
# Usuario y contraseña definidos por el usuario, asumimos permisos de creación de DB.
SERVER_CREDS = {
    "host": "localhost",
    "user": "user",
    "password": "user123",
    "db_name": "negocio"
}

# Puertos configurados en Docker para cada motor
SERVER_CONFIGS = {
    "PostgreSQL": {"port": 5432, "driver": "psycopg2", "initial_db": "postgres"},
    "MySQL":      {"port": 3306, "driver": "mysql", "initial_db": None}, 
    "MariaDB":    {"port": 3308, "driver": "mysql", "initial_db": None},
}

# --- SENTENCIAS SQL (MySQL / MariaDB) ---
# Usadas en los puertos 3306 y 3308.
SQL_MYSQL = """
-- Tabla Usuario
CREATE TABLE IF NOT EXISTS Usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(150),
    fechaDeRegistro DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- Tabla Zona
CREATE TABLE IF NOT EXISTS Zona (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    numeroIncidencias INT DEFAULT 0,
    coordenadas VARCHAR(255)
);
-- Tabla Reporte
CREATE TABLE IF NOT EXISTS Reporte (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_zona INT,
    tipoIncidencia VARCHAR(100),
    descripcion TEXT,
    fechaHora DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(50),
    prioridad VARCHAR(20),
    medioReporte VARCHAR(50),
    ubicacion VARCHAR(150),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_zona) REFERENCES Zona(id) ON DELETE CASCADE
);
-- Tabla Comentario
CREATE TABLE IF NOT EXISTS Comentario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_reporte INT,
    texto TEXT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_reporte) REFERENCES Reporte(id) ON DELETE CASCADE
);
-- Tabla Multimedia
CREATE TABLE IF NOT EXISTS Multimedia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_reporte INT,
    tipoArchivo VARCHAR(50),
    rutaArchivo VARCHAR(255),
    FOREIGN KEY (id_reporte) REFERENCES Reporte(id) ON DELETE CASCADE
);
-- Tabla Alerta
CREATE TABLE IF NOT EXISTS Alerta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_reporte INT,
    tipo VARCHAR(50),
    mensaje TEXT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_reporte) REFERENCES Reporte(id) ON DELETE CASCADE
);
-- Tabla Sensor
CREATE TABLE IF NOT EXISTS Sensor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_zona INT,
    tipo VARCHAR(50),
    ubicacion VARCHAR(150),
    fechaInstalacion DATE,
    modelo VARCHAR(50),
    estado VARCHAR(50),
    FOREIGN KEY (id_zona) REFERENCES Zona(id) ON DELETE CASCADE
);
-- Tabla RegistroSensor
CREATE TABLE IF NOT EXISTS RegistroSensor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_sensor INT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    valor DECIMAL(10,2),
    unidad VARCHAR(20),
    FOREIGN KEY (id_sensor) REFERENCES Sensor(id) ON DELETE CASCADE
);
-- Tabla Indicador
CREATE TABLE IF NOT EXISTS Indicador (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_zona INT,
    id_registro_sensor INT,
    nombre VARCHAR(100),
    descripcion TEXT,
    valor DECIMAL(10,2),
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_zona) REFERENCES Zona(id) ON DELETE CASCADE,
    FOREIGN KEY (id_registro_sensor) REFERENCES RegistroSensor(id) ON DELETE CASCADE
);
-- Tabla Informe
CREATE TABLE IF NOT EXISTS Informe (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_indicador INT,
    titulo VARCHAR(100),
    descripcion TEXT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(50),
    fuentes TEXT,
    FOREIGN KEY (id_indicador) REFERENCES Indicador(id) ON DELETE CASCADE
);
"""

# --- SENTENCIAS SQL (PostgreSQL) ---
# Usada en el puerto 5432.
SQL_PG = """
-- Tabla Usuario
CREATE TABLE IF NOT EXISTS Usuario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(150),
    fechaDeRegistro TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Tabla Zona
CREATE TABLE IF NOT EXISTS Zona (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    numeroIncidencias INT DEFAULT 0,
    coordenadas VARCHAR(255)
);
-- Tabla Reporte
CREATE TABLE IF NOT EXISTS Reporte (
    id SERIAL PRIMARY KEY,
    id_usuario INT,
    id_zona INT,
    tipoIncidencia VARCHAR(100),
    descripcion TEXT,
    fechaHora TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(50),
    prioridad VARCHAR(20),
    medioReporte VARCHAR(50),
    ubicacion VARCHAR(150),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_zona) REFERENCES Zona(id) ON DELETE CASCADE
);
-- Tabla Comentario
CREATE TABLE IF NOT EXISTS Comentario (
    id SERIAL PRIMARY KEY,
    id_usuario INT,
    id_reporte INT,
    texto TEXT,
    fecha TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_reporte) REFERENCES Reporte(id) ON DELETE CASCADE
);
-- Tabla Multimedia
CREATE TABLE IF NOT EXISTS Multimedia (
    id SERIAL PRIMARY KEY,
    id_reporte INT,
    tipoArchivo VARCHAR(50),
    rutaArchivo VARCHAR(255),
    FOREIGN KEY (id_reporte) REFERENCES Reporte(id) ON DELETE CASCADE
);
-- Tabla Alerta
CREATE TABLE IF NOT EXISTS Alerta (
    id SERIAL PRIMARY KEY,
    id_reporte INT,
    tipo VARCHAR(50),
    mensaje TEXT,
    fecha TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_reporte) REFERENCES Reporte(id) ON DELETE CASCADE
);
-- Tabla Sensor
CREATE TABLE IF NOT EXISTS Sensor (
    id SERIAL PRIMARY KEY,
    id_zona INT,
    tipo VARCHAR(50),
    ubicacion VARCHAR(150),
    fechaInstalacion DATE,
    modelo VARCHAR(50),
    estado VARCHAR(50),
    FOREIGN KEY (id_zona) REFERENCES Zona(id) ON DELETE CASCADE
);
-- Tabla RegistroSensor
CREATE TABLE IF NOT EXISTS RegistroSensor (
    id SERIAL PRIMARY KEY,
    id_sensor INT,
    fecha TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    valor DECIMAL(10,2),
    unidad VARCHAR(20),
    FOREIGN KEY (id_sensor) REFERENCES Sensor(id) ON DELETE CASCADE
);
-- Tabla Indicador
CREATE TABLE IF NOT EXISTS Indicador (
    id SERIAL PRIMARY KEY,
    id_zona INT,
    id_registro_sensor INT,
    nombre VARCHAR(100),
    descripcion TEXT,
    valor DECIMAL(10,2),
    fecha TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_zona) REFERENCES Zona(id) ON DELETE CASCADE,
    FOREIGN KEY (id_registro_sensor) REFERENCES RegistroSensor(id) ON DELETE CASCADE
);
-- Tabla Informe
CREATE TABLE IF NOT EXISTS Informe (
    id SERIAL PRIMARY KEY,
    id_indicador INT,
    titulo VARCHAR(100),
    descripcion TEXT,
    fecha TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(50),
    fuentes TEXT,
    FOREIGN KEY (id_indicador) REFERENCES Indicador(id) ON DELETE CASCADE
);
"""
# --- FUNCIONES DE CONEXIÓN Y CREACIÓN ---

def create_db_and_schema(db_name, config):
    """Crea la base de datos y su esquema para un motor específico."""
    
    print(f"\n--- Procesando {db_name} (Puerto {config['port']}) ---")
    conn = None
    
    try:
        if config["driver"] == "psycopg2":
            # Lógica para PostgreSQL
            # Conexión inicial al servidor (usando la DB 'postgres' por defecto)
            conn = psycopg2.connect(
                host=SERVER_CREDS["host"], port=config["port"],
                user=SERVER_CREDS["user"], password=SERVER_CREDS["password"],
                database=config["initial_db"]
            )
            conn.autocommit = True
            cursor = conn.cursor()

            print(f"    1. Eliminando y creando DB '{SERVER_CREDS['db_name']}'...")
            try:
                # Intenta forzar la eliminación, ignorando el error si no existe
                cursor.execute(f"DROP DATABASE IF EXISTS {SERVER_CREDS['db_name']} WITH (FORCE)") 
            except:
                pass 
            cursor.execute(f"CREATE DATABASE {SERVER_CREDS['db_name']}")
            cursor.close()
            conn.close()

            # Reconexión a la nueva base de datos para crear las tablas
            conn = psycopg2.connect(
                host=SERVER_CREDS["host"], port=config["port"],
                user=SERVER_CREDS["user"], password=SERVER_CREDS["password"],
                database=SERVER_CREDS["db_name"]
            )
            cursor = conn.cursor()
            
            print("    2. Creando todas las tablas...")
            cursor.execute(SQL_PG)
            conn.commit()
            print("Estructura creada correctamente.")
            
        elif config["driver"] == "mysql":
            # Lógica para MySQL/MariaDB
            # Conexión inicial al servidor (sin especificar base de datos)
            conn = mysql.connector.connect(
                host=SERVER_CREDS["host"], port=config["port"],
                user=SERVER_CREDS["user"], password=SERVER_CREDS["password"]
            )
            cursor = conn.cursor()

            print(f"    1. Eliminando y creando DB '{SERVER_CREDS['db_name']}'...")
            cursor.execute(f"DROP DATABASE IF EXISTS {SERVER_CREDS['db_name']}")
            cursor.execute(f"CREATE DATABASE {SERVER_CREDS['db_name']}")
            conn.commit()
            
            cursor.execute(f"USE {SERVER_CREDS['db_name']}")
            
            print("    2. Creando todas las tablas...")
            # Ejecución del esquema SQL (dividiendo por sentencias)
            for statement in SQL_MYSQL.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            
            conn.commit()
            print("Estructura creada correctamente.")
            
    except Exception as e:
        print(f"ERROR en {db_name} (Puerto {config['port']}): {e}")
    finally:
        if conn: conn.close()


def main():
    print("--- INICIO DE LA CREACIÓN DE ESTRUCTURAS DE BASES DE DATOS ---")
    
    # Procesar PostgreSQL
    create_db_and_schema("PostgreSQL", SERVER_CONFIGS["PostgreSQL"])
    
    # Procesar MySQL
    create_db_and_schema("MySQL", SERVER_CONFIGS["MySQL"])

    # Procesar MariaDB
    create_db_and_schema("MariaDB", SERVER_CONFIGS["MariaDB"])

    print("\n--- PROCESO FINALIZADO ---")

if __name__ == "__main__":
    main()