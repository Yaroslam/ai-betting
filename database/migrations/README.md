# 🗄️ База данных CS2 Match Prediction System

## 📋 **Обзор**

Профессиональная структура базы данных для системы прогнозирования матчей CS2 с использованием ChatGPT. База данных спроектирована с соблюдением принципов нормализации (3NF) и оптимизирована для высокой производительности.

## 🏗️ **Архитектура**

### ✅ **Принципы проектирования**
- **Нормализация**: Соблюдение 3-й нормальной формы
- **ACID**: Полная поддержка транзакционности
- **Производительность**: Оптимизированные индексы и запросы
- **Масштабируемость**: Готовность к росту данных
- **Целостность**: Строгие ограничения и проверки

### 📊 **Структура данных**

#### 🔗 **Основные сущности**
- **13 таблиц** с четкой иерархией зависимостей
- **30+ индексов** для оптимизации запросов
- **JSONB поля** для гибкого хранения метаданных

#### 📈 **Статистика парсера HLTV**
База данных полностью совместима с данными, которые собирает ваш HLTV парсер:

**Команды:**
- ✅ HLTV ID, название, тег, страна
- ✅ Рейтинг, очки, логотип
- ✅ Ссылка на HLTV профиль

**Игроки:**
- ✅ HLTV ID, ник, настоящее имя
- ✅ Возраст, страна, аватар
- ✅ Роль в команде, история переходов

**Статистика игроков:**
- ✅ Rating 2.0, K/D ratio, ADR, KAST
- ✅ Процент хедшотов, карты сыграны
- ✅ Убийства/ассисты/смерти за раунд
- ✅ Периодическое обновление данных

## 🚀 **Быстрый старт**

### 1️⃣ **Запуск миграций**
```bash
# Создание схемы базы данных через миграции
php bin/migrate.php up

# Загрузка тестовых данных
php bin/migrate.php up --target=20250625061216
```

### 2️⃣ **Проверка установки**
```sql
-- Проверка созданных таблиц
\dt

-- Проверка данных
SELECT COUNT(*) FROM teams;
SELECT COUNT(*) FROM players;
SELECT COUNT(*) FROM matches;
```

## 📊 **Диаграмма базы данных**

Полная ERD диаграмма показывает все связи между таблицами:

![Database Schema](DATABASE_SCHEMA.md)

## 🔍 **Примеры использования**

### Получить топ-10 игроков по рейтингу
```sql
SELECT 
    p.nickname,
    p.real_name,
    c.name as country,
    ps.rating_2_0,
    ps.maps_played
FROM players p
JOIN player_statistics ps ON p.id = ps.player_id
JOIN countries c ON p.country_id = c.id
WHERE ps.period_end = (SELECT MAX(period_end) FROM player_statistics)
ORDER BY ps.rating_2_0 DESC
LIMIT 10;
```

### Получить предстоящие матчи с прогнозами
```sql
SELECT 
    m.scheduled_at,
    t1.name as team1,
    t2.name as team2,
    e.name as event,
    mp.predicted_winner_id,
    tw.name as predicted_winner,
    mp.confidence_percentage,
    mp.prediction_text
FROM matches m
JOIN teams t1 ON m.team1_id = t1.id
JOIN teams t2 ON m.team2_id = t2.id
JOIN events e ON m.event_id = e.id
LEFT JOIN match_predictions mp ON m.id = mp.match_id
LEFT JOIN teams tw ON mp.predicted_winner_id = tw.id
WHERE m.status = 'scheduled'
    AND m.scheduled_at > NOW()
ORDER BY m.scheduled_at;
```

### Статистика точности прогнозов
```sql
SELECT 
    COUNT(*) as total_predictions,
    COUNT(CASE WHEN is_correct = true THEN 1 END) as correct_predictions,
    ROUND(
        COUNT(CASE WHEN is_correct = true THEN 1 END)::decimal / 
        COUNT(CASE WHEN is_correct IS NOT NULL THEN 1 END) * 100, 2
    ) as accuracy_percentage,
    AVG(confidence_percentage) as avg_confidence
FROM match_predictions
WHERE is_correct IS NOT NULL;
```

## 📁 **Структура файлов**

```
database/migrations/
├── 📄 DATABASE_SCHEMA.md     # Подробная документация
├── 📄 README.md              # Этот файл
├── 📄 QUICKSTART.md          # Краткое руководство
├── 📄 env.example            # Пример настроек
├── 📄 composer.json          # PHP зависимости
├── 🗂️ bin/                   # Скрипты миграций
└── 🗂️ migrations/            # Файлы миграций
    ├── postgres/             # PostgreSQL миграции
    │   ├── up/              # Миграции "вверх"
    │   └── down/            # Миграции "вниз"
    └── clickhouse/          # ClickHouse миграции
        ├── up/              # Миграции "вверх"
        └── down/            # Миграции "вниз"
```

## 🛠️ **Интеграция с микросервисами**

### 🐍 **HLTV Parser (Python)**
```python
# Пример интеграции с парсером
def save_team_data(team_data):
    query = """
    INSERT INTO teams (hltv_id, name, tag, country_id, world_ranking, points, hltv_url)
    VALUES (%(hltv_id)s, %(name)s, %(tag)s, %(country_id)s, %(ranking)s, %(points)s, %(url)s)
    ON CONFLICT (hltv_id) DO UPDATE SET
        name = EXCLUDED.name,
        world_ranking = EXCLUDED.world_ranking,
        points = EXCLUDED.points,
        updated_at = CURRENT_TIMESTAMP
    """
    cursor.execute(query, team_data)
```

### 🤖 **Telegram Bot**
```python
# Пример получения данных для бота
def get_upcoming_matches():
    query = """
    SELECT m.*, t1.name as team1, t2.name as team2, 
           mp.prediction_text, mp.confidence_percentage
    FROM matches m
    JOIN teams t1 ON m.team1_id = t1.id
    JOIN teams t2 ON m.team2_id = t2.id
    LEFT JOIN match_predictions mp ON m.id = mp.match_id
    WHERE m.status = 'scheduled' AND m.scheduled_at > NOW()
    ORDER BY m.scheduled_at
    LIMIT 5
    """
    return cursor.fetchall()
```

### 💰 **Payment Service (PHP)**
```php
// Пример обработки платежа
function processPremiumPayment($userId, $amount) {
    $pdo->beginTransaction();
    try {
        // Создаем запись о платеже
        $stmt = $pdo->prepare("
            INSERT INTO payments (user_id, amount, payment_type, status) 
            VALUES (?, ?, 'premium_subscription', 'completed')
        ");
        $stmt->execute([$userId, $amount]);
        
        // Обновляем статус пользователя
        $stmt = $pdo->prepare("
            UPDATE users 
            SET is_premium = true, premium_until = NOW() + INTERVAL '1 month'
            WHERE id = ?
        ");
        $stmt->execute([$userId]);
        
        $pdo->commit();
    } catch (Exception $e) {
        $pdo->rollback();
        throw $e;
    }
}
```

## 🔧 **Настройка окружения**

### PostgreSQL конфигурация
```bash
# Создание базы данных
createdb cs2_prediction

# Создание пользователя
createuser cs2_user

# Назначение прав
GRANT ALL PRIVILEGES ON DATABASE cs2_prediction TO cs2_user;
```

### Переменные окружения
```bash
# Скопируйте и настройте
cp env.example .env

# Основные настройки
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cs2_prediction
POSTGRES_USER=cs2_user
POSTGRES_PASSWORD=your_password
```

## 📈 **Мониторинг и оптимизация**

### Полезные запросы для мониторинга
```sql
-- Размер таблиц
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::text)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::text) DESC;

-- Активность индексов
SELECT 
    indexrelname,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_tup_read DESC;

-- Медленные запросы
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

## 🛡️ **Безопасность**

### Рекомендации по безопасности
- ✅ Используйте подготовленные запросы (prepared statements)
- ✅ Ограничьте права доступа пользователей БД
- ✅ Регулярно создавайте резервные копии
- ✅ Мониторьте подозрительную активность
- ✅ Используйте SSL соединения в продакшене

### Резервное копирование
```bash
# Создание бэкапа
pg_dump -h localhost -U cs2_user cs2_prediction > backup_$(date +%Y%m%d).sql

# Восстановление из бэкапа
psql -h localhost -U cs2_user cs2_prediction < backup_20241201.sql
```

## 📞 **Поддержка**

При возникновении вопросов или проблем:

1. **Проверьте логи PostgreSQL**
2. **Убедитесь в корректности настроек подключения**
3. **Проверьте права доступа пользователя БД**
4. **Изучите документацию в `DATABASE_SCHEMA.md`**

---

**🎯 База данных готова к использованию!** Вы можете начинать интеграцию с вашими микросервисами. 