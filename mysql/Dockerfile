
FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=admin123
ENV MYSQL_DATABASE=negocio
ENV MYSQL_USER=user
ENV MYSQL_PASSWORD=user123

COPY ./inicio.sql /docker-entrypoint-initdb.d/

EXPOSE 3306

VOLUME ["/var/lib/mysql"]

CMD ["mysqld"]
