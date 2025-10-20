-- *** Este script es compatible con MariaDB y MySQL. ***
-- Nota: Las sentencias CREATE DATABASE y USE negocio; se eliminan porque Docker las gestiona.

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