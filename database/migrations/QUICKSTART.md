# 🚀 Быстрый старт: Laravel-style система миграций

Laravel-подобная система миграций для PostgreSQL и ClickHouse с полной поддержкой отката.

## ⚡ **Установка за 3 шага**

### 1️⃣ Установка зависимостей

```bash
cd database/migrations
composer install
```

### 2️⃣ Настройка окружения

```bash
# Скопировать настройки
cp .env.example .env

# Отредактировать под ваши БД
nano .env
```

### 3️⃣ Первый запуск

```bash
# Проверить статус PostgreSQL миграций
php artisan migrate:status

# Проверить статус ClickHouse миграций
php artisan migrate:clickhouse
```

## 🎯 **Основные команды PostgreSQL**

### Создание миграций

```bash
# Создать новую миграцию
php artisan make:migration create_users_table

# Создать миграцию для новой таблицы
php artisan make:migration create_users_table --create=users

# Создать миграцию для изменения таблицы
php artisan make:migration add_email_to_users_table --table=users
```

### Выполнение миграций

```bash
# Выполнить все ожидающие миграции
php artisan migrate

# Принудительное выполнение в production
php artisan migrate --force
```

### Проверка статуса

```bash
# Показать статус всех миграций
php artisan migrate:status
```

### Откат миграций

```bash
# Откатить последний батч миграций
php artisan migrate:rollback

# Откатить определенное количество миграций
php artisan migrate:rollback --steps=3

# Откатить все миграции
php artisan migrate:reset

# Откатить все и выполнить заново
php artisan migrate:refresh
```

## 🎯 **Основные команды ClickHouse**

### Создание миграций

```bash
# Создать новую ClickHouse миграцию
php artisan make:clickhouse-migration create_events_table
```

### Выполнение миграций

```bash
# Выполнить все ClickHouse миграции
php artisan migrate:clickhouse

# Принудительное выполнение в production
php artisan migrate:clickhouse --force
```

## 📝 **Пример: Создание таблицы пользователей PostgreSQL**

### Шаг 1: Создать миграцию

```bash
php artisan make:migration create_users_table --create=users
```

### Шаг 2: Отредактировать файл миграции

**migrations/2025_06_25_220000_create_users_table.php:**

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->string('username')->unique();
            $table->string('email')->unique();
            $table->bigInteger('telegram_id')->unique()->nullable();
            $table->string('password_hash');
            $table->decimal('balance', 10, 2)->default(0.00);
            $table->boolean('is_premium')->default(false);
            $table->timestamps();
            
            // Indexes
            $table->index('username');
            $table->index('email');
            $table->index('telegram_id');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('users');
    }
};
```

### Шаг 3: Применить миграцию

```bash
php artisan migrate
```

## 📊 **Пример: Аналитическая таблица ClickHouse**

### Шаг 1: Создать ClickHouse миграцию

```bash
php artisan make:clickhouse-migration create_user_events
```

### Шаг 2: Отредактировать файл миграции

**clickhouse-migrations/2025_06_25_220100_create_user_events.php:**

```php
<?php

use Database\Migrations\ClickHouseMigration;

return new class extends ClickHouseMigration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        $this->createTable('user_events', '
            id UInt64,
            user_id UInt64,
            event_type LowCardinality(String),
            event_data String,
            timestamp DateTime64(3),
            session_id String,
            ip_address IPv4,
            user_agent String,
            created_at DateTime DEFAULT now()
        ', 'MergeTree()', '(event_type, timestamp, user_id)');
        
        // Добавляем индексы для быстрого поиска
        $this->addIndex('user_events', 'idx_user_id', 'user_id', 'bloom_filter');
        $this->addIndex('user_events', 'idx_session_id', 'session_id', 'bloom_filter');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        $this->dropTable('user_events');
    }
};
```

### Шаг 3: Применить миграцию

```bash
php artisan migrate:clickhouse
```

## 🔧 **Composer скрипты (быстрые команды)**

```bash
# PostgreSQL
composer run migrate                    # Применить миграции
composer run migrate:status             # Статус миграций
composer run migrate:rollback           # Откатить последний батч
composer run migrate:reset              # Сбросить все миграции
composer run migrate:refresh            # Сбросить и применить заново

# ClickHouse  
composer run migrate:clickhouse         # Применить ClickHouse миграции

# Создание миграций
composer run make:migration             # Создать PostgreSQL миграцию
composer run make:clickhouse-migration  # Создать ClickHouse миграцию
```

## 🗂️ **Структура файлов**

После создания миграций у вас будет:

```
database/migrations/
├── .env                              # Ваши настройки БД
├── .env.example                      # Пример настроек
├── artisan                           # Главный файл команд
├── composer.json                     # Зависимости
├── src/
│   ├── Commands/                     # Команды миграций
│   │   ├── MigrateMakeCommand.php
│   │   ├── MigrateCommand.php
│   │   ├── MigrateStatusCommand.php
│   │   ├── MigrateRollbackCommand.php
│   │   ├── MigrateResetCommand.php
│   │   ├── MigrateRefreshCommand.php
│   │   ├── ClickHouseMigrateCommand.php
│   │   └── ClickHouseMakeMigrationCommand.php
│   └── ClickHouseMigration.php       # Базовый класс для ClickHouse
├── migrations/                       # PostgreSQL миграции
│   └── 2025_06_25_220000_create_users_table.php
├── clickhouse-migrations/            # ClickHouse миграции
│   └── 2025_06_25_220100_create_user_events.php
└── seeders/                         # Сидеры (будущие)
```

## ⚙️ **Настройка .env файла**

```bash
# Application
APP_ENV=development
APP_DEBUG=true

# PostgreSQL Configuration (Main Database)
DB_CONNECTION=pgsql
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=cs2_predictions
DB_USERNAME=postgres
DB_PASSWORD=postgres

# ClickHouse Configuration (Analytics Database)
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_DATABASE=analytics
CLICKHOUSE_USERNAME=clickhouse
CLICKHOUSE_PASSWORD=clickhouse

# Migration Settings
MIGRATION_TABLE=migrations
CLICKHOUSE_MIGRATION_TABLE=clickhouse_migrations
```

## 🔄 **Рабочий процесс разработки**

### 1. Создание новой функции

```bash
# 1. Создать миграцию PostgreSQL
php artisan make:migration create_matches_table --create=matches

# 2. Создать миграцию ClickHouse для аналитики
php artisan make:clickhouse-migration create_match_analytics

# 3. Отредактировать файлы миграций
# 4. Применить миграции
php artisan migrate
php artisan migrate:clickhouse
```

### 2. Изменение существующей структуры

```bash
# 1. Создать миграцию для изменения
php artisan make:migration add_status_to_matches_table --table=matches

# 2. Применить миграцию
php artisan migrate

# 3. Если что-то пошло не так - откатить
php artisan migrate:rollback
```

### 3. Проверка состояния

```bash
# Проверить статус всех миграций
php artisan migrate:status

# Сбросить все и применить заново (осторожно!)
php artisan migrate:refresh --force
```

## 💡 **Особенности новой системы**

### ✅ **Преимущества:**

- **Историчность**: Все миграции сохраняются в хронологическом порядке
- **Откат**: Полная поддержка отката миграций для PostgreSQL
- **Laravel-style**: Знакомый синтаксис для разработчиков Laravel
- **Раздельность**: Отдельные системы для PostgreSQL и ClickHouse
- **Батчи**: Группировка миграций по батчам для удобного отката
- **Автоматизация**: Автоматическое создание таблиц миграций

### 🎯 **Рекомендации:**

- Всегда тестируйте миграции на тестовой БД
- Делайте резервные копии перед применением в production
- Используйте `--force` флаг только в production окружении
- Пишите понятные имена миграций
- Всегда реализуйте метод `down()` для возможности отката 