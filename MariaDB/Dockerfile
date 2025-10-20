FROM mariadb:10.11

# Variables de entorno utilizando el prefijo MARIADB_
ENV MARIADB_ROOT_PASSWORD=admin123
ENV MARIADB_DATABASE=negocio
ENV MARIADB_USER=user
ENV MARIADB_PASSWORD=user123

# Copia el script SQL de inicialización
COPY ./inicio.sql /docker-entrypoint-initdb.d/

EXPOSE 3306

# Define el punto de montaje del volumen (Es el mismo que MySQL)
VOLUME ["/var/lib/mariadb"]