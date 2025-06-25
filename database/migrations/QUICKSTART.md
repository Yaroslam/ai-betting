# 🚀 Быстрый старт: Единая PHP система миграций

Быстрое начало работы с миграциями для PostgreSQL и ClickHouse на чистом PHP.

## ⚡ **Установка за 3 шага**

### 1️⃣ Установка зависимостей

```bash
cd database/migrations
composer install
```

### 2️⃣ Настройка окружения

```bash
# Скопировать настройки
cp env.example .env

# Отредактировать под ваши БД
nano .env
```

### 3️⃣ Первый запуск

```bash
# Проверить подключение к PostgreSQL
php bin/migrate.php postgres status

# Проверить подключение к ClickHouse  
php bin/migrate.php clickhouse status
```

## 🎯 **Основные команды**

### Создание миграций

```bash
# PostgreSQL - основная БД
php bin/migrate.php postgres create "create_users_table"

# ClickHouse - аналитика
php bin/migrate.php clickhouse create "create_events_table"
```

### Выполнение миграций

```bash
# Применить все PostgreSQL миграции
php bin/migrate.php postgres migrate

# Применить все ClickHouse миграции
php bin/migrate.php clickhouse migrate
```

### Проверка статуса

```bash
# Статус PostgreSQL
php bin/migrate.php postgres status

# Статус ClickHouse
php bin/migrate.php clickhouse status
```

## 📝 **Пример: Создание таблицы пользователей**

### Шаг 1: Создать миграцию

```bash
php bin/migrate.php postgres create "create_users_table"
```

### Шаг 2: Написать SQL (файл создается автоматически)

**migrations/postgres/up/20241201120000_create_users_table.sql:**

```sql
-- Up migration: create_users_table
-- PostgreSQL Migration

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    telegram_id BIGINT UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    balance DECIMAL(10,2) DEFAULT 0.00,
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
```

**migrations/postgres/down/20241201120000.sql:**

```sql
-- Down migration: create_users_table
-- PostgreSQL Migration

DROP TABLE IF EXISTS users;
```

### Шаг 3: Применить миграцию

```bash
php bin/migrate.php postgres migrate
```

## 📊 **Пример: Аналитическая таблица**

### Создать ClickHouse миграцию

```bash
php bin/migrate.php clickhouse create "create_user_events"
```

**migrations/clickhouse/up/20241201130000_create_user_events.sql:**

```sql
-- Up migration: create_user_events
-- ClickHouse Migration

CREATE TABLE user_events (
    id UInt64,
    user_id UInt64,
    event_type LowCardinality(String),
    event_data String, -- JSON
    timestamp DateTime64(3),
    session_id String,
    ip_address IPv4,
    user_agent String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (event_type, timestamp, user_id)
PARTITION BY toYYYYMM(timestamp)
SETTINGS index_granularity = 8192;

-- Дополнительные индексы для быстрого поиска
ALTER TABLE user_events ADD INDEX idx_user_id user_id TYPE bloom_filter GRANULARITY 1;
ALTER TABLE user_events ADD INDEX idx_session_id session_id TYPE bloom_filter GRANULARITY 1;
```

## 🔧 **Composer скрипты (быстрые команды)**

```bash
# PostgreSQL
composer run migrate:postgres              # Применить миграции
composer run migrate:status:postgres       # Статус
composer run migrate:reset:postgres        # Сброс БД

# ClickHouse  
composer run migrate:clickhouse            # Применить миграции
composer run migrate:status:clickhouse     # Статус
composer run migrate:reset:clickhouse      # Сброс БД
```

## 🗂️ **Структура файлов**

После создания миграций у вас будет:

```
database/migrations/
├── .env                              # Ваши настройки БД
├── migrations/
│   ├── postgres/
│   │   ├── up/
│   │   │   └── 20241201120000_create_users_table.sql
│   │   └── down/
│   │       └── 20241201120000.sql
│   └── clickhouse/
│       ├── up/
│       │   └── 20241201130000_create_user_events.sql
│       └── down/
│           └── 20241201130000.sql
└── bin/migrate.php                   # Основной скрипт
```

## ⚙️ **Настройка .env файла**

```bash
# PostgreSQL (основная БД)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cs2_prediction
POSTGRES_USER=cs2_user
POSTGRES_PASSWORD=your_secure_password

# ClickHouse (аналитика)
CLICKHOUSE_HOST=localhost
CLICKHOUSE_HTTP_PORT=8123
CLICKHOUSE_DB=cs2_analytics
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
```

## 🚨 **Частые проблемы и решения**

### ❌ "Database connection failed"

**Решение:**
1. Проверьте настройки в `.env`
2. Убедитесь, что БД запущена
3. Проверьте права доступа

### ❌ "Migration table not found"

**Решение:**
```bash
# Создать таблицу версий вручную
php bin/migrate.php postgres reset
php bin/migrate.php clickhouse reset
```

### ❌ "Permission denied"

**Решение:**
```bash
# Дать права на выполнение
chmod +x bin/migrate.php
```

## 🎉 **Готово!**

Теперь у вас есть единая система миграций для обеих баз данных!

### Следующие шаги:

1. **Создайте базовые таблицы** для вашего проекта
2. **Настройте CI/CD** для автоматического выполнения миграций
3. **Изучите документацию** в README.md для продвинутых функций

### Полезные команды для разработки:

```bash
# Проверить все статусы одной командой
php bin/migrate.php postgres status && php bin/migrate.php clickhouse status

# Применить все миграции одной командой  
php bin/migrate.php postgres migrate && php bin/migrate.php clickhouse migrate

# Создать миграции для новой функции
php bin/migrate.php postgres create "add_matches_table"
php bin/migrate.php clickhouse create "add_match_analytics"
```

**Удачной разработки! 🚀** 