# HLTV Парсеры

Набор парсеров для извлечения данных с сайта HLTV.org

## Описание

Проект содержит два основных парсера:
1. **PlayerParser** - для парсинга профилей игроков
2. **TeamParser** - для парсинга рейтинга команд

## Парсеры

### PlayerParser

Парсер профилей игроков с HLTV.org.

#### Что парсит:
- Базовая информация: никнейм, настоящее имя, страна, возраст
- Игровая статистика:
  - Rating 2.0
  - Impact
  - ADR (Average Damage per Round)
  - K/D Ratio
  - KAST (Percentage of rounds with Kill, Assist, Survive or Trade)
  - DPR (Deaths per Round)
  - KPR (Kills per Round)
  - Количество сыгранных карт

#### Использование:
```python
from player_parser import PlayerParser

with PlayerParser() as parser:
    # Парсинг игрока по ID и никнейму
    player_data = parser.parse_player(20425, 'r1nkle')
    
    if player_data:
        print(f"Игрок: {player_data['nickname']}")
        print(f"Rating 2.0: {player_data['statistics']['rating_2_0']}")
        
        # Сохранение в базу данных
        parser.save_player_to_database(player_data)
```

### TeamParser

Парсер рейтинга команд с HLTV.org.

#### Что парсит:
- Информация о команде: название, место в рейтинге, очки
- Состав команды (автоматически парсит каждого игрока)
- Ссылки на профили игроков

#### Использование:
```python
from team_parser import TeamParser

with TeamParser() as parser:
    # Парсинг топ-30 команд
    teams = parser.parse_team_ranking(max_teams=30)
    
    # Сохранение всех команд в базу данных
    saved_count = parser.save_all_teams_to_database(teams)
    print(f"Сохранено команд: {saved_count}")
```

## Технические детали

### Архитектура
- Использует Selenium WebDriver с headless Firefox
- Обход блокировок через настройку профиля браузера
- Retry механизм для надежности
- Интеграция с SQLAlchemy для работы с PostgreSQL

### Настройки браузера
- Headless режим для скрытой работы
- Отключение загрузки изображений для ускорения
- Настройка User-Agent для обхода детекции
- Отключение WebDriver флагов

### База данных
Парсеры сохраняют данные в следующие таблицы:
- `players` - информация об игроках
- `player_statistics` - статистика игроков
- `teams` - информация о командах
- `team_rosters` - составы команд

## Установка и запуск

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск тестов
```bash
# Тест парсера игроков
python src/test_single_player.py

# Полный тест обоих парсеров
python src/main.py
```

## Конфигурация

### Переменные окружения
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Настройки парсера
- `max_teams` - максимальное количество команд для парсинга
- `retries` - количество попыток при неудачных запросах
- `timeout` - время ожидания загрузки страницы

## Логирование

Все парсеры ведут подробные логи:
- Информация о загрузке страниц
- Извлеченные данные
- Ошибки и исключения
- Статус сохранения в базу данных

## Обработка ошибок

Парсеры включают обработку следующих ошибок:
- Timeout при загрузке страниц
- Блокировка доступа (403 ошибки)
- Недоступность элементов на странице
- Ошибки подключения к базе данных

## Примеры использования

### Парсинг конкретного игрока
```python
from player_parser import PlayerParser

with PlayerParser() as parser:
    player_data = parser.parse_player(20425, 'r1nkle')
    if player_data:
        print(f"Rating 2.0: {player_data['statistics']['rating_2_0']}")
```

### Парсинг топ-5 команд
```python
from team_parser import TeamParser

with TeamParser() as parser:
    teams = parser.parse_team_ranking(max_teams=5)
    for team in teams:
        print(f"#{team['rank']}: {team['name']} - {team['points']} очков")
```

## Ограничения

- HLTV может блокировать частые запросы
- Необходимо соблюдать разумные интервалы между запросами
- Структура сайта может изменяться, требуя обновления селекторов
- Требуется стабильное интернет-соединение

## Поддержка

При возникновении проблем:
1. Проверьте логи парсера
2. Убедитесь в доступности HLTV.org
3. Проверьте настройки базы данных
4. Обновите браузер и драйвер geckodriver 