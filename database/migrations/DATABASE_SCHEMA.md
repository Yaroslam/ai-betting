# 🗄️ Структура базы данных CS2 Match Prediction System

## 📋 **Обзор**

База данных спроектирована с соблюдением принципов нормализации (3NF) и содержит всю необходимую информацию для системы прогнозирования матчей CS2. Структура оптимизирована для быстрого поиска и аналитических запросов.

## 🏗️ **Архитектурные принципы**

### ✅ **Соблюдение нормальных форм**
- **1NF**: Все атрибуты атомарны, нет повторяющихся групп
- **2NF**: Устранены частичные зависимости от составных ключей
- **3NF**: Устранены транзитивные зависимости

### 🔗 **ACID свойства**
- **Атомарность**: Все операции выполняются полностью или не выполняются вообще
- **Согласованность**: Все ограничения целостности соблюдаются
- **Изолированность**: Параллельные транзакции не влияют друг на друга
- **Долговечность**: Зафиксированные изменения сохраняются

### 🚀 **Оптимизация производительности**
- Индексы на часто используемые поля
- Партиционирование больших таблиц (при необходимости)
- Денормализация для аналитических запросов
- Оптимизированные JOIN-ы через внешние ключи

## 📊 **Структура таблиц**

### 1. 📚 **Справочные таблицы (Reference Tables)**

#### `countries` - Справочник стран
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
code VARCHAR(3) UNIQUE             -- ISO 3166-1 alpha-3 код
name VARCHAR(100)                  -- Название страны
flag_url VARCHAR(255)              -- URL флага
created_at TIMESTAMP               -- Дата создания
```

**Назначение**: Нормализация данных о странах команд и игроков.

#### `maps` - Игровые карты CS2
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
name VARCHAR(50) UNIQUE            -- Название карты (de_dust2)
display_name VARCHAR(100)          -- Отображаемое название (Dust II)
image_url VARCHAR(255)             -- URL изображения карты
is_active BOOLEAN                  -- Активна ли карта в пуле
created_at TIMESTAMP               -- Дата создания
```

**Назначение**: Справочник игровых карт для матчей.

#### `event_types` - Типы турниров
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
name VARCHAR(100) UNIQUE           -- Название типа турнира
tier VARCHAR(20)                   -- Уровень турнира (S, A, B, C)
created_at TIMESTAMP               -- Дата создания
```

**Назначение**: Классификация турниров по важности и престижу.

### 2. 🏢 **Основные сущности (Core Entities)**

#### `teams` - Команды CS2
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
hltv_id INTEGER UNIQUE             -- ID команды на HLTV.org
name VARCHAR(100)                  -- Название команды
tag VARCHAR(10)                    -- Короткий тег (NAVI, G2)
country_id INTEGER FK              -- Ссылка на страну
logo_url VARCHAR(255)              -- URL логотипа
hltv_url VARCHAR(255)              -- Ссылка на HLTV
world_ranking INTEGER              -- Мировой рейтинг
points INTEGER                     -- Рейтинговые очки
is_active BOOLEAN                  -- Активна ли команда
created_at TIMESTAMP               -- Дата создания
updated_at TIMESTAMP               -- Дата обновления
```

**Особенности**:
- Индексы на `hltv_id`, `world_ranking`, `is_active`
- Связь с парсером HLTV через `hltv_id`

#### `players` - Игроки CS2
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
hltv_id INTEGER UNIQUE             -- ID игрока на HLTV.org
nickname VARCHAR(50)               -- Игровой ник
real_name VARCHAR(100)             -- Настоящее имя
country_id INTEGER FK              -- Ссылка на страну
age INTEGER CHECK (age > 0 < 100)  -- Возраст с проверкой
avatar_url VARCHAR(255)            -- URL аватара
hltv_url VARCHAR(255)              -- Ссылка на HLTV
is_active BOOLEAN                  -- Активен ли игрок
created_at TIMESTAMP               -- Дата создания  
updated_at TIMESTAMP               -- Дата обновления
```

**Особенности**:
- Проверочные ограничения на возраст
- Связь с парсером через `hltv_id`

#### `team_rosters` - Составы команд
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
team_id INTEGER FK                 -- Ссылка на команду
player_id INTEGER FK               -- Ссылка на игрока
role VARCHAR(50)                   -- Роль (IGL, AWPer, Support)
is_active BOOLEAN                  -- Активен ли в составе
joined_at TIMESTAMP                -- Дата присоединения
left_at TIMESTAMP NULL             -- Дата ухода (NULL если активен)
created_at TIMESTAMP               -- Дата создания записи
```

**Особенности**:
- Уникальность по `(team_id, player_id, joined_at)`
- История изменений составов
- Каскадное удаление при удалении команды/игрока

### 3. 📈 **Статистика игроков**

#### `player_statistics` - Статистика игроков по периодам
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
player_id INTEGER FK               -- Ссылка на игрока

-- Основные показатели из HLTV
rating_2_0 DECIMAL(4,3)            -- Рейтинг 2.0 (1.234)
kd_ratio DECIMAL(4,3)              -- Kill/Death ratio
adr DECIMAL(5,2)                   -- Average Damage per Round
kast DECIMAL(5,2)                  -- KAST percentage
headshot_percentage DECIMAL(5,2)   -- Процент хедшотов

-- Детальная статистика
maps_played INTEGER                -- Количество сыгранных карт
kills_per_round DECIMAL(4,3)       -- Убийств за раунд
assists_per_round DECIMAL(4,3)     -- Ассистов за раунд
deaths_per_round DECIMAL(4,3)      -- Смертей за раунд
saved_by_teammate_per_round DECIMAL(4,3)  -- Спасений командой
saved_teammates_per_round DECIMAL(4,3)    -- Спасений команды

-- Временные рамки
period_start DATE                  -- Начало периода
period_end DATE                    -- Конец периода
last_updated TIMESTAMP             -- Последнее обновление
created_at TIMESTAMP               -- Дата создания
```

**Особенности**:
- Уникальность по `(player_id, period_start, period_end)`
- Периодическое обновление из парсера HLTV
- Индексы для быстрого поиска по рейтингу

### 4. 🏆 **Турниры и события**

#### `events` - Турниры/события
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
hltv_id INTEGER UNIQUE             -- ID события на HLTV.org
name VARCHAR(200)                  -- Название турнира
event_type_id INTEGER FK           -- Тип турнира
start_date DATE                    -- Дата начала
end_date DATE                      -- Дата окончания
prize_pool INTEGER                 -- Призовой фонд в USD
location VARCHAR(100)              -- Место проведения
hltv_url VARCHAR(255)              -- Ссылка на HLTV
is_completed BOOLEAN               -- Завершен ли турнир
created_at TIMESTAMP               -- Дата создания
updated_at TIMESTAMP               -- Дата обновления
```

### 5. ⚔️ **Матчи**

#### `matches` - Матчи между командами
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
hltv_id INTEGER UNIQUE             -- ID матча на HLTV.org
event_id INTEGER FK                -- Ссылка на турнир

-- Участники
team1_id INTEGER FK                -- Первая команда
team2_id INTEGER FK                -- Вторая команда
CHECK (team1_id != team2_id)       -- Команды должны быть разными

-- Результат
team1_score INTEGER                -- Счет первой команды
team2_score INTEGER                -- Счет второй команды
winner_id INTEGER FK               -- Победитель (NULL если не завершен)
CHECK (winner_id IN (team1_id, team2_id) OR winner_id IS NULL)

-- Детали
match_format VARCHAR(20)           -- Bo1, Bo3, Bo5
match_type VARCHAR(50)             -- Group Stage, Final и т.д.
scheduled_at TIMESTAMP             -- Запланированное время
started_at TIMESTAMP               -- Время начала
ended_at TIMESTAMP                 -- Время окончания

-- Статус
status VARCHAR(20)                 -- scheduled, live, completed, cancelled
hltv_url VARCHAR(255)              -- Ссылка на HLTV
created_at TIMESTAMP               -- Дата создания
updated_at TIMESTAMP               -- Дата обновления
```

**Особенности**:
- Проверочные ограничения на логику матча
- Индексы для поиска матчей между командами

#### `match_maps` - Карты в матчах
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
match_id INTEGER FK                -- Ссылка на матч
map_id INTEGER FK                  -- Ссылка на карту
map_number INTEGER                 -- Порядковый номер в матче
CHECK (map_number > 0)             -- Номер должен быть положительным

-- Результат по карте
team1_rounds INTEGER               -- Раунды первой команды
team2_rounds INTEGER               -- Раунды второй команды
winner_id INTEGER FK               -- Победитель карты

-- Статус
status VARCHAR(20)                 -- upcoming, live, completed
created_at TIMESTAMP               -- Дата создания
```

**Особенности**:
- Уникальность по `(match_id, map_number)`
- Проверка корректности победителя через подзапрос
- Каскадное удаление при удалении матча

### 6. 🔮 **Прогнозы**

#### `match_predictions` - Прогнозы от ChatGPT
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
match_id INTEGER FK                -- Ссылка на матч (UNIQUE)

-- Прогноз
predicted_winner_id INTEGER FK     -- Предсказанный победитель
confidence_percentage DECIMAL(5,2) -- Уверенность (0-100%)
CHECK (confidence_percentage >= 0 AND confidence_percentage <= 100)
predicted_score VARCHAR(10)        -- Предсказанный счет (2-1)

-- Текст прогноза
prediction_text TEXT               -- Основной текст прогноза
reasoning TEXT                     -- Обоснование прогноза
analyzed_factors JSONB             -- JSON с факторами анализа

-- Результат прогноза
is_correct BOOLEAN                 -- Верен ли прогноз (NULL до завершения)
actual_winner_id INTEGER FK        -- Фактический победитель
actual_score VARCHAR(10)           -- Фактический счет

created_at TIMESTAMP               -- Дата создания
updated_at TIMESTAMP               -- Дата обновления
```

**Особенности**:
- Один прогноз на матч (UNIQUE constraint)
- JSONB для гибкого хранения факторов анализа
- Проверочные ограничения на процент уверенности
- Отслеживание точности прогнозов

### 7. 👥 **Пользователи и платежи**

#### `users` - Пользователи Telegram бота
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
telegram_id BIGINT UNIQUE          -- ID пользователя в Telegram

-- Профиль
username VARCHAR(100)              -- Username в Telegram
first_name VARCHAR(100)            -- Имя
last_name VARCHAR(100)             -- Фамилия
email VARCHAR(255) UNIQUE          -- Email (опционально)

-- Подписка
is_premium BOOLEAN DEFAULT FALSE   -- Премиум статус
premium_until TIMESTAMP            -- До какого времени премиум

-- Баланс
balance DECIMAL(10,2) DEFAULT 0.00 -- Баланс пользователя
CHECK (balance >= 0)               -- Баланс не может быть отрицательным

-- Настройки
notification_settings JSONB DEFAULT '{}'  -- Настройки уведомлений

-- Статус
is_active BOOLEAN DEFAULT TRUE     -- Активен ли аккаунт
is_banned BOOLEAN DEFAULT FALSE    -- Заблокирован ли

-- Метаданные
created_at TIMESTAMP               -- Дата регистрации
updated_at TIMESTAMP               -- Дата обновления профиля
last_activity TIMESTAMP            -- Последняя активность
```

#### `payments` - История платежей
```sql
id SERIAL PRIMARY KEY              -- Внутренний ID
user_id INTEGER FK                 -- Ссылка на пользователя

-- Платеж
amount DECIMAL(10,2)               -- Сумма платежа
CHECK (amount > 0)                 -- Сумма должна быть положительной
currency VARCHAR(3) DEFAULT 'USD'  -- Валюта
payment_type VARCHAR(50)           -- Тип: premium_subscription, balance_topup

-- Статус
status VARCHAR(20) DEFAULT 'pending' -- pending, completed, failed, refunded

-- Внешние системы
external_payment_id VARCHAR(255)   -- ID в платежной системе
payment_method VARCHAR(50)         -- Способ оплаты: card, crypto

-- Метаданные
metadata JSONB                     -- Дополнительная информация
created_at TIMESTAMP               -- Дата создания
updated_at TIMESTAMP               -- Дата обновления
```

## 🔍 **Индексы для производительности**

### Основные индексы:
```sql
-- Команды
CREATE INDEX idx_teams_hltv_id ON teams(hltv_id);
CREATE INDEX idx_teams_world_ranking ON teams(world_ranking);
CREATE INDEX idx_teams_is_active ON teams(is_active);

-- Игроки  
CREATE INDEX idx_players_hltv_id ON players(hltv_id);
CREATE INDEX idx_players_is_active ON players(is_active);

-- Матчи
CREATE INDEX idx_matches_scheduled_at ON matches(scheduled_at);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_teams ON matches(team1_id, team2_id);

-- Статистика
CREATE INDEX idx_player_statistics_rating ON player_statistics(rating_2_0 DESC);
CREATE INDEX idx_player_statistics_period ON player_statistics(period_start, period_end);

-- Пользователи
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_is_premium ON users(is_premium);
```



## 📊 **Примеры запросов**

### Получить топ-10 игроков по рейтингу:
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

### Получить предстоящие матчи с прогнозами:
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

### Статистика точности прогнозов:
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

## 🛡️ **Безопасность и целостность**

### Ограничения целостности:
- **Внешние ключи**: Все связи между таблицами защищены FK constraints
- **Проверочные ограничения**: Валидация данных на уровне БД
- **Уникальные ключи**: Предотвращение дублирования
- **NOT NULL**: Обязательные поля защищены от NULL значений

### Каскадные операции:
- `ON DELETE CASCADE`: Автоматическое удаление зависимых записей
- `ON UPDATE CASCADE`: Автоматическое обновление связанных данных

## 📈 **Масштабирование**

### Стратегии оптимизации:
1. **Партиционирование**: Разделение больших таблиц по датам
2. **Индексирование**: Составные индексы для сложных запросов  
3. **Денормализация**: Материализованные представления для аналитики
4. **Архивирование**: Перенос старых данных в архивные таблицы

### Мониторинг производительности:
- Анализ планов выполнения запросов
- Мониторинг использования индексов
- Отслеживание медленных запросов
- Статистика использования таблиц 