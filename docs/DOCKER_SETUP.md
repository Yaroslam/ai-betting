# Docker Infrastructure Setup

Данный документ описывает настройку Docker инфраструктуры для CS2 Prediction System.

## Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   ClickHouse    │    │   RabbitMQ      │
│   Port: 5432    │    │   Port: 8123    │    │   Port: 5672    │
│   cs2_postgres  │    │   cs2_clickhouse│    │   cs2_rabbitmq  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                        cs2_network (172.20.0.0/16)
```

## Компоненты

### 1. PostgreSQL
- **Контейнер**: `cs2_postgres`
- **Порт**: 5432
- **База данных**: `cs2_predictions` (создается автоматически)
- **Пользователь**: `postgres` / `postgres`
- **Примечание**: Структура БД создается отдельно миграциями

### 2. ClickHouse
- **Контейнер**: `cs2_clickhouse`
- **Порты**: 8123 (HTTP), 9000 (Native), 9009 (Interserver)
- **База данных**: `analytics` (создается автоматически)
- **Пользователь**: `clickhouse` / `clickhouse`
- **Примечание**: Таблицы создаются отдельно миграциями

### 3. RabbitMQ
- **Контейнер**: `cs2_rabbitmq`
- **Порты**: 5672 (AMQP), 15672 (Management)
- **Пользователь**: `rabbitmq` / `rabbitmq`
- **Exchanges**: `cs2.matches`, `cs2.predictions`, `cs2.payments`, `cs2.analytics`

## Быстрый запуск

### Linux/macOS
```bash
# Дать права на выполнение скриптам
chmod +x scripts/start-infrastructure.sh
chmod +x scripts/stop-infrastructure.sh

# Запуск инфраструктуры
./scripts/start-infrastructure.sh
```

### Windows
```batch
# Запуск через PowerShell или Command Prompt
scripts\start-infrastructure.bat
```

### Ручной запуск
```bash
# Только инфраструктура
docker-compose -f infrastructure/docker-compose.infrastructure.yml up -d

# Или полный стек
docker-compose up -d
```

## Проверка состояния

После запуска проверьте доступность сервисов:

### PostgreSQL
```bash
# Проверка подключения
docker exec cs2_postgres pg_isready -U postgres -d cs2_predictions

# Подключение к базе
docker exec -it cs2_postgres psql -U postgres -d cs2_predictions
```

### ClickHouse
```bash
# Проверка HTTP интерфейса
curl http://localhost:8123/ping

# Подключение к базе
docker exec -it cs2_clickhouse clickhouse-client --user clickhouse --password clickhouse --database analytics
```

### RabbitMQ
```bash
# Проверка статуса
docker exec cs2_rabbitmq rabbitmq-diagnostics -q ping

# Management UI
# Откройте http://localhost:15672 в браузере
# Логин: rabbitmq, Пароль: rabbitmq
```

## Volumes и данные

### Persistent Volumes
- `postgres_data`: данные PostgreSQL
- `clickhouse_data`: данные ClickHouse
- `rabbitmq_data`: данные RabbitMQ

### Log Volumes
- `postgres_logs`: логи PostgreSQL
- `clickhouse_logs`: логи ClickHouse
- `rabbitmq_logs`: логи RabbitMQ

### Просмотр логов
```bash
# Все сервисы
docker-compose -f infrastructure/docker-compose.infrastructure.yml logs

# Конкретный сервис
docker-compose -f infrastructure/docker-compose.infrastructure.yml logs postgresql
docker-compose -f infrastructure/docker-compose.infrastructure.yml logs clickhouse
docker-compose -f infrastructure/docker-compose.infrastructure.yml logs rabbitmq
```

## Конфигурационные файлы

### PostgreSQL
- `infrastructure/docker/postgresql/postgresql.conf` - основная конфигурация
- `infrastructure/docker/postgresql/pg_hba.conf` - настройки аутентификации

### ClickHouse
- `infrastructure/docker/clickhouse/config.xml` - основная конфигурация
- `infrastructure/docker/clickhouse/users.xml` - пользователи и права

### RabbitMQ
- `infrastructure/docker/rabbitmq/rabbitmq.conf` - основная конфигурация
- `infrastructure/docker/rabbitmq/definitions.json` - exchanges, queues, bindings
- `infrastructure/docker/rabbitmq/enabled_plugins` - включенные плагины

## Сеть

### Docker Network
- **Имя**: `cs2_network`
- **Подсеть**: `172.20.0.0/16`
- **Тип**: bridge

### Внутренние адреса
- PostgreSQL: `cs2_postgres:5432`
- ClickHouse: `cs2_clickhouse:8123`, `cs2_clickhouse:9000`
- RabbitMQ: `cs2_rabbitmq:5672`

## Полезные команды

### Управление контейнерами
```bash
# Просмотр статуса
docker ps --filter name=cs2

# Остановка всех сервисов
docker-compose -f infrastructure/docker-compose.infrastructure.yml down

# Перезапуск конкретного сервиса
docker-compose -f infrastructure/docker-compose.infrastructure.yml restart postgresql

# Пересборка образов
docker-compose -f infrastructure/docker-compose.infrastructure.yml build --no-cache
```

### Бэкап и восстановление
```bash
# Бэкап PostgreSQL
docker exec cs2_postgres pg_dump -U postgres cs2_predictions > backup_postgres.sql

# Бэкап ClickHouse
docker exec cs2_clickhouse clickhouse-client --query "BACKUP DATABASE analytics TO Disk('default', 'backup_clickhouse')"

# Очистка старых данных
docker system prune -f
docker volume prune -f
```

## Troubleshooting

### Проблемы с PostgreSQL
- Проверьте логи: `docker logs cs2_postgres`
- Убедитесь, что порт 5432 не занят другими процессами
- Проверьте права доступа к volumes

### Проблемы с ClickHouse
- Проверьте логи: `docker logs cs2_clickhouse`
- Убедитесь, что порты 8123, 9000 свободны
- Проверьте настройки ulimits для nofile

### Проблемы с RabbitMQ
- Проверьте логи: `docker logs cs2_rabbitmq`
- Убедитесь, что порты 5672, 15672 свободны
- Проверьте конфигурацию в definitions.json

### Проблемы с сетью
- Проверьте Docker networks: `docker network ls`
- Очистите старые сети: `docker network prune`
- Проверьте конфликты подсетей

## Мониторинг

### Health Checks
Все контейнеры настроены с health checks:
```bash
# Проверка статуса
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Метрики
- RabbitMQ Management UI: http://localhost:15672
- ClickHouse системные таблицы: `system.*`
- PostgreSQL статистика: `pg_stat_*` 