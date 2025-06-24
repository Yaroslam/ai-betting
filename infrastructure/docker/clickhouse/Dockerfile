FROM clickhouse/clickhouse-server:latest

# Установка дополнительных пакетов
USER root
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование конфигурационных файлов
COPY ./config.xml /etc/clickhouse-server/config.xml
COPY ./users.xml /etc/clickhouse-server/users.xml

# Установка прав доступа
RUN chown -R clickhouse:clickhouse /etc/clickhouse-server/

# Переключение обратно на пользователя clickhouse
USER clickhouse

# Переменные окружения
ENV CLICKHOUSE_DB=analytics
ENV CLICKHOUSE_USER=clickhouse
ENV CLICKHOUSE_PASSWORD=clickhouse

# Порты
EXPOSE 8123 9000 9009

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8123/ping || exit 1 