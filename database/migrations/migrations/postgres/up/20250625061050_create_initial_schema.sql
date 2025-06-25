-- Up migration: create_initial_schema
-- PostgreSQL Migration
-- CS2 Match Prediction System - Initial Database Schema

-- =====================================================
-- 1. СПРАВОЧНЫЕ ТАБЛИЦЫ (Reference Tables)
-- =====================================================

-- Страны
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) NOT NULL UNIQUE, -- ISO 3166-1 alpha-3 (например: RUS, USA, GER)
    name VARCHAR(100) NOT NULL,
    flag_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Игровые карты CS2
CREATE TABLE maps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- de_dust2, de_mirage и т.д.
    display_name VARCHAR(100) NOT NULL, -- Dust II, Mirage и т.д.
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Типы турниров/событий
CREATE TABLE event_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE, -- Major, ESL Pro League, BLAST Premier и т.д.
    tier VARCHAR(20) NOT NULL, -- S, A, B, C
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2. ОСНОВНЫЕ СУЩНОСТИ (Core Entities)
-- =====================================================

-- Команды
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    hltv_id INTEGER UNIQUE, -- ID команды на HLTV.org
    name VARCHAR(100) NOT NULL,
    tag VARCHAR(10), -- Короткий тег команды (например: NAVI, G2)
    country_id INTEGER REFERENCES countries(id),
    logo_url VARCHAR(255),
    hltv_url VARCHAR(255), -- Ссылка на страницу команды на HLTV
    world_ranking INTEGER, -- Текущий рейтинг команды в мире
    points INTEGER DEFAULT 0, -- Рейтинговые очки
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Игроки
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    hltv_id INTEGER UNIQUE, -- ID игрока на HLTV.org
    nickname VARCHAR(50) NOT NULL,
    real_name VARCHAR(100),
    country_id INTEGER REFERENCES countries(id),
    age INTEGER CHECK (age > 0 AND age < 100),
    avatar_url VARCHAR(255),
    hltv_url VARCHAR(255), -- Ссылка на страницу игрока на HLTV
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Состав команд (многие ко многим с историей)
CREATE TABLE team_rosters (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    role VARCHAR(50), -- IGL, AWPer, Entry Fragger, Support, Lurker
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(team_id, player_id, joined_at)
);

-- =====================================================
-- 3. СТАТИСТИКА ИГРОКОВ (Player Statistics)
-- =====================================================

-- Статистика игроков (периодически обновляемая из HLTV)
CREATE TABLE player_statistics (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    
    -- Основные показатели
    rating_2_0 DECIMAL(4,3), -- Рейтинг 2.0 (например: 1.234)
    kd_ratio DECIMAL(4,3), -- Kill/Death ratio
    adr DECIMAL(5,2), -- Average Damage per Round
    kast DECIMAL(5,2), -- Kill, Assist, Survive, Trade percentage
    headshot_percentage DECIMAL(5,2), -- Процент хедшотов
    
    -- Детальная статистика
    maps_played INTEGER DEFAULT 0,
    kills_per_round DECIMAL(4,3),
    assists_per_round DECIMAL(4,3),
    deaths_per_round DECIMAL(4,3),
    saved_by_teammate_per_round DECIMAL(4,3),
    saved_teammates_per_round DECIMAL(4,3),
    
    -- Метаданные
    period_start DATE NOT NULL, -- Начало периода статистики
    period_end DATE NOT NULL, -- Конец периода статистики
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(player_id, period_start, period_end)
);

-- =====================================================
-- 4. ТУРНИРЫ И СОБЫТИЯ (Tournaments & Events)
-- =====================================================

-- Турниры/события
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    hltv_id INTEGER UNIQUE, -- ID события на HLTV.org
    name VARCHAR(200) NOT NULL,
    event_type_id INTEGER REFERENCES event_types(id),
    start_date DATE,
    end_date DATE,
    prize_pool INTEGER, -- Призовой фонд в USD
    location VARCHAR(100), -- Место проведения
    hltv_url VARCHAR(255),
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 5. МАТЧИ (Matches)
-- =====================================================

-- Матчи
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    hltv_id INTEGER UNIQUE, -- ID матча на HLTV.org
    event_id INTEGER REFERENCES events(id),
    
    -- Команды
    team1_id INTEGER NOT NULL REFERENCES teams(id),
    team2_id INTEGER NOT NULL REFERENCES teams(id),
    
    -- Результат
    team1_score INTEGER,
    team2_score INTEGER,
    winner_id INTEGER REFERENCES teams(id), -- NULL если матч не завершен
    
    -- Детали матча
    match_format VARCHAR(20), -- Bo1, Bo3, Bo5
    match_type VARCHAR(50), -- Group Stage, Quarterfinal, Semifinal, Final и т.д.
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    
    -- Статус
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, live, completed, cancelled, postponed
    
    -- Метаданные
    hltv_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (team1_id != team2_id),
    CHECK (winner_id IN (team1_id, team2_id) OR winner_id IS NULL)
);

-- Карты в матче
CREATE TABLE match_maps (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    map_id INTEGER NOT NULL REFERENCES maps(id),
    map_number INTEGER NOT NULL, -- Порядковый номер карты в матче (1, 2, 3...)
    
    -- Счет по карте
    team1_rounds INTEGER,
    team2_rounds INTEGER,
    winner_id INTEGER REFERENCES teams(id),
    
    -- Статус карты
    status VARCHAR(20) DEFAULT 'upcoming', -- upcoming, live, completed
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(match_id, map_number),
    CHECK (map_number > 0),
    CHECK (winner_id IN (
        (SELECT team1_id FROM matches WHERE id = match_id),
        (SELECT team2_id FROM matches WHERE id = match_id)
    ) OR winner_id IS NULL)
);

-- =====================================================
-- 6. ПРОГНОЗЫ И ПРЕДСКАЗАНИЯ (Predictions)
-- =====================================================

-- Прогнозы от ChatGPT
CREATE TABLE match_predictions (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    
    -- Прогноз
    predicted_winner_id INTEGER NOT NULL REFERENCES teams(id),
    confidence_percentage DECIMAL(5,2) CHECK (confidence_percentage >= 0 AND confidence_percentage <= 100),
    predicted_score VARCHAR(10), -- Например: "2-1", "2-0"
    
    -- Текст прогноза от ChatGPT
    prediction_text TEXT NOT NULL,
    reasoning TEXT, -- Обоснование прогноза
    
    -- Факторы анализа
    analyzed_factors JSONB, -- JSON с факторами: форма команд, хед-ту-хед и т.д.
    
    -- Результат прогноза
    is_correct BOOLEAN, -- NULL пока матч не завершен
    actual_winner_id INTEGER REFERENCES teams(id),
    actual_score VARCHAR(10),
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(match_id) -- Один прогноз на матч
);

-- =====================================================
-- 7. ПОЛЬЗОВАТЕЛИ И ПОДПИСКИ (Users & Subscriptions)
-- =====================================================

-- Пользователи
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE, -- ID пользователя в Telegram
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    
    -- Подписка
    is_premium BOOLEAN DEFAULT FALSE,
    premium_until TIMESTAMP,
    
    -- Баланс
    balance DECIMAL(10,2) DEFAULT 0.00 CHECK (balance >= 0),
    
    -- Настройки уведомлений
    notification_settings JSONB DEFAULT '{}',
    
    -- Статус
    is_active BOOLEAN DEFAULT TRUE,
    is_banned BOOLEAN DEFAULT FALSE,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- История платежей
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Платеж
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'USD',
    payment_type VARCHAR(50) NOT NULL, -- premium_subscription, balance_topup
    
    -- Статус
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, failed, refunded
    
    -- Внешние ID
    external_payment_id VARCHAR(255), -- ID в платежной системе
    payment_method VARCHAR(50), -- card, crypto, etc.
    
    -- Метаданные
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 8. ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ
-- =====================================================

-- Индексы для команд
CREATE INDEX idx_teams_hltv_id ON teams(hltv_id);
CREATE INDEX idx_teams_country_id ON teams(country_id);
CREATE INDEX idx_teams_world_ranking ON teams(world_ranking);
CREATE INDEX idx_teams_is_active ON teams(is_active);

-- Индексы для игроков
CREATE INDEX idx_players_hltv_id ON players(hltv_id);
CREATE INDEX idx_players_country_id ON players(country_id);
CREATE INDEX idx_players_is_active ON players(is_active);

-- Индексы для состава команд
CREATE INDEX idx_team_rosters_team_id ON team_rosters(team_id);
CREATE INDEX idx_team_rosters_player_id ON team_rosters(player_id);
CREATE INDEX idx_team_rosters_is_active ON team_rosters(is_active);

-- Индексы для статистики игроков
CREATE INDEX idx_player_statistics_player_id ON player_statistics(player_id);
CREATE INDEX idx_player_statistics_period ON player_statistics(period_start, period_end);
CREATE INDEX idx_player_statistics_rating ON player_statistics(rating_2_0 DESC);

-- Индексы для матчей
CREATE INDEX idx_matches_hltv_id ON matches(hltv_id);
CREATE INDEX idx_matches_event_id ON matches(event_id);
CREATE INDEX idx_matches_team1_id ON matches(team1_id);
CREATE INDEX idx_matches_team2_id ON matches(team2_id);
CREATE INDEX idx_matches_scheduled_at ON matches(scheduled_at);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_teams ON matches(team1_id, team2_id); -- Для поиска матчей между командами

-- Индексы для карт матчей
CREATE INDEX idx_match_maps_match_id ON match_maps(match_id);
CREATE INDEX idx_match_maps_map_id ON match_maps(map_id);

-- Индексы для прогнозов
CREATE INDEX idx_match_predictions_match_id ON match_predictions(match_id);
CREATE INDEX idx_match_predictions_predicted_winner ON match_predictions(predicted_winner_id);
CREATE INDEX idx_match_predictions_is_correct ON match_predictions(is_correct);

-- Индексы для пользователей
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_premium ON users(is_premium);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Индексы для платежей
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- =====================================================
-- 9. КОММЕНТАРИИ К ТАБЛИЦАМ
-- =====================================================

COMMENT ON TABLE countries IS 'Справочник стран для команд и игроков';
COMMENT ON TABLE maps IS 'Игровые карты CS2';
COMMENT ON TABLE event_types IS 'Типы турниров и событий';
COMMENT ON TABLE teams IS 'Команды CS2 с данными из HLTV';
COMMENT ON TABLE players IS 'Игроки CS2 с данными из HLTV';
COMMENT ON TABLE team_rosters IS 'История составов команд';
COMMENT ON TABLE player_statistics IS 'Статистика игроков за определенные периоды';
COMMENT ON TABLE events IS 'Турниры и события';
COMMENT ON TABLE matches IS 'Матчи между командами';
COMMENT ON TABLE match_maps IS 'Карты, сыгранные в матчах';
COMMENT ON TABLE match_predictions IS 'Прогнозы от ChatGPT для матчей';
COMMENT ON TABLE users IS 'Пользователи Telegram бота';
COMMENT ON TABLE payments IS 'История платежей пользователей';

