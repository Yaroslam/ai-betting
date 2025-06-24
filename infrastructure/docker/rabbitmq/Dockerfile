FROM rabbitmq:3-management-alpine

# Установка дополнительных пакетов
RUN apk add --no-cache curl

# Включение необходимых плагинов
RUN rabbitmq-plugins enable --offline rabbitmq_management \
    rabbitmq_management_agent \
    rabbitmq_web_dispatch \
    rabbitmq_amqp1_0 \
    rabbitmq_mqtt \
    rabbitmq_stomp \
    rabbitmq_auth_backend_ldap \
    rabbitmq_consistent_hash_exchange \
    rabbitmq_federation \
    rabbitmq_federation_management \
    rabbitmq_shovel \
    rabbitmq_shovel_management

# Копирование конфигурационных файлов
COPY ./rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
COPY ./definitions.json /etc/rabbitmq/definitions.json
COPY ./enabled_plugins /etc/rabbitmq/enabled_plugins

# Установка прав доступа
RUN chown -R rabbitmq:rabbitmq /etc/rabbitmq/

# Переменные окружения
ENV RABBITMQ_DEFAULT_USER=rabbitmq
ENV RABBITMQ_DEFAULT_PASS=rabbitmq
ENV RABBITMQ_DEFAULT_VHOST=/
ENV RABBITMQ_MANAGEMENT_LOAD_DEFINITIONS=/etc/rabbitmq/definitions.json

# Порты
EXPOSE 5672 15672 25672 15692

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD rabbitmq-diagnostics -q ping 