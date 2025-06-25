-- Down migration: create_initial_schema
-- PostgreSQL Migration

-- Удаляем все в обратном порядке зависимостей

-- Удаляем таблицы в обратном порядке зависимостей
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS match_predictions CASCADE;
DROP TABLE IF EXISTS match_maps CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS player_statistics CASCADE;
DROP TABLE IF EXISTS team_rosters CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS event_types CASCADE;
DROP TABLE IF EXISTS maps CASCADE;
DROP TABLE IF EXISTS countries CASCADE;

