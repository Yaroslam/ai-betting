# CS2 Match Prediction System

Система предсказания результатов матчей Counter-Strike 2 с использованием искусственного интеллекта (ChatGPT).

## Описание

Микросервисная система, которая:
- Парсит данные матчей с HLTV.org
- Анализирует их с помощью OpenAI API (ChatGPT)
- Предоставляет прогнозы через Telegram бота
- Обрабатывает платежи за премиум подписку
- Показывает аналитику точности предсказаний

## Архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HLTV Parser   │    │  Prediction      │    │  Telegram Bot   │
│   (Python)      │────│  Service (Go)    │────│   (Python)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────▼────────┐              │
         │              │   RabbitMQ      │              │
         │              │  (Message Bus)  │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   ClickHouse     │    │ Payment Service │
│  (Main Data)    │    │   (Analytics)    │    │     (PHP)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │ Analytics Web   │
                       │    (Scala)      │
                       └─────────────────┘
```

## Сервисы

### 1. HLTV Parser (Python)
- Парсинг матчей, команд, статистики с HLTV.org
- Сохранение данных в PostgreSQL
- Отправка событий в RabbitMQ

### 2. Telegram Bot (Python)
- Интерфейс для пользователей
- Получение запросов на прогнозы
- Отображение результатов
- Обработка подписок

### 3. Prediction Service (Go)
- Обработка запросов на прогнозы
- Интеграция с OpenAI API
- Анализ исторических данных
- Генерация предсказаний

### 4. Payment Service (PHP)
- Обработка платежей
- Управление подписками
- Webhook обработка
- Интеграция с платежными системами

### 5. Analytics Web (Scala)
- Веб-интерфейс для аналитики
- Отчеты по точности предсказаний
- Графики и статистика
- Панель администратора

## Базы данных

- **PostgreSQL**: основные данные (матчи, команды, пользователи, подписки)
- **ClickHouse**: аналитические данные (статистика, метрики, логи)

## Быстрый запуск

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd ai-betting
```

2. Скопируйте и настройте переменные окружения:
```bash
cp env.example .env
# Отредактируйте .env файл с вашими ключами API
```

3. Запустите инфраструктуру:
```bash
docker-compose up -d postgresql clickhouse rabbitmq
```

4. Запустите все сервисы:
```bash
docker-compose up -d
```

## Разработка

### Структура проекта
```
ai-betting/
├── services/
│   ├── hltv-parser/          # Python парсер HLTV
│   ├── telegram-bot/         # Python Telegram бот
│   ├── prediction-service/   # Go сервис предсказаний
│   ├── payment-service/      # PHP сервис платежей
│   └── analytics-web/        # Scala веб аналитика
├── infrastructure/
│   ├── docker/              # Docker конфигурации
│   └── rabbitmq/            # RabbitMQ настройки
├── docs/                    # Документация
└── scripts/                 # Скрипты автоматизации
```

### Технологии
- **Python**: FastAPI, aiogram, SQLAlchemy, BeautifulSoup4
- **Go**: Gin, GORM, RabbitMQ client
- **PHP**: Laravel/Symfony, Composer
- **Scala**: Play Framework, Akka
- **Базы данных**: PostgreSQL, ClickHouse
- **Инфраструктура**: Docker, RabbitMQ

## API Интеграции

- **OpenAI API**: для анализа и генерации прогнозов
- **Telegram Bot API**: для взаимодействия с пользователями
- **Payment APIs**: для обработки платежей

## Лицензия

Проект разрабатывается для образовательных целей.

## Контрибьюция

1. Форкните проект
2. Создайте ветку для новой функции
3. Сделайте коммит изменений
4. Создайте Pull Request 