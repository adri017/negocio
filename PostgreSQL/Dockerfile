FROM postgres:15-alpine

# Variables de entorno para la configuración inicial
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=user123
ENV POSTGRES_DB=negocio

# Copia el script SQL de inicialización
COPY ./inicio.sql /docker-entrypoint-initdb.d/init.sql

# Define el punto de montaje del volumen para la persistencia de datos
# Este es el directorio interno de PostgreSQL donde guarda los datos.
VOLUME ["/var/lib/postgresql/data"]

EXPOSE 5432