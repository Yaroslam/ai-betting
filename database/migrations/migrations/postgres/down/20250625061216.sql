-- Down migration: insert_initial_data
-- PostgreSQL Migration

-- Удаляем все тестовые данные в обратном порядке зависимостей

-- Удаляем прогнозы
DELETE FROM match_predictions;

-- Удаляем матчи и карты
DELETE FROM match_maps;
DELETE FROM matches;

-- Удаляем события
DELETE FROM events;

-- Удаляем статистику игроков
DELETE FROM player_statistics;

-- Удаляем составы команд
DELETE FROM team_rosters;

-- Удаляем игроков
DELETE FROM players;

-- Удаляем команды
DELETE FROM teams;

-- Удаляем справочные данные
DELETE FROM event_types;
DELETE FROM maps;
DELETE FROM countries;

