FROM postgres:15-alpine

# Установка дополнительных пакетов
RUN apk add --no-cache \
    curl \
    postgresql-contrib

# Копирование конфигурационных файлов
COPY ./postgresql.conf /etc/postgresql/postgresql.conf
COPY ./pg_hba.conf /etc/postgresql/pg_hba.conf

# Переменные окружения по умолчанию
ENV POSTGRES_DB=cs2_predictions
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Порт
EXPOSE 5432

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB 