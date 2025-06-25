-- Up migration: insert_initial_data
-- PostgreSQL Migration

-- =====================================================
-- СПРАВОЧНЫЕ ДАННЫЕ (Reference Data)
-- =====================================================

-- Страны (основные страны CS2 сцены)
INSERT INTO countries (code, name, flag_url) VALUES
('RUS', 'Russia', 'https://www.hltv.org/img/static/flags/30x20/RU.gif'),
('UKR', 'Ukraine', 'https://www.hltv.org/img/static/flags/30x20/UA.gif'),
('USA', 'United States', 'https://www.hltv.org/img/static/flags/30x20/US.gif'),
('FRA', 'France', 'https://www.hltv.org/img/static/flags/30x20/FR.gif'),
('GER', 'Germany', 'https://www.hltv.org/img/static/flags/30x20/DE.gif'),
('DEN', 'Denmark', 'https://www.hltv.org/img/static/flags/30x20/DK.gif'),
('SWE', 'Sweden', 'https://www.hltv.org/img/static/flags/30x20/SE.gif'),
('NOR', 'Norway', 'https://www.hltv.org/img/static/flags/30x20/NO.gif'),
('FIN', 'Finland', 'https://www.hltv.org/img/static/flags/30x20/FI.gif'),
('POL', 'Poland', 'https://www.hltv.org/img/static/flags/30x20/PL.gif'),
('BRA', 'Brazil', 'https://www.hltv.org/img/static/flags/30x20/BR.gif'),
('AUS', 'Australia', 'https://www.hltv.org/img/static/flags/30x20/AU.gif'),
('CAN', 'Canada', 'https://www.hltv.org/img/static/flags/30x20/CA.gif'),
('GBR', 'United Kingdom', 'https://www.hltv.org/img/static/flags/30x20/GB.gif'),
('ESP', 'Spain', 'https://www.hltv.org/img/static/flags/30x20/ES.gif'),
('NLD', 'Netherlands', 'https://www.hltv.org/img/static/flags/30x20/NL.gif'),
('BEL', 'Belgium', 'https://www.hltv.org/img/static/flags/30x20/BE.gif'),
('CZE', 'Czech Republic', 'https://www.hltv.org/img/static/flags/30x20/CZ.gif'),
('SVK', 'Slovakia', 'https://www.hltv.org/img/static/flags/30x20/SK.gif'),
('TUR', 'Turkey', 'https://www.hltv.org/img/static/flags/30x20/TR.gif'),
('KAZ', 'Kazakhstan', 'https://www.hltv.org/img/static/flags/30x20/KZ.gif'),
('CHN', 'China', 'https://www.hltv.org/img/static/flags/30x20/CN.gif'),
('JPN', 'Japan', 'https://www.hltv.org/img/static/flags/30x20/JP.gif'),
('KOR', 'South Korea', 'https://www.hltv.org/img/static/flags/30x20/KR.gif'),
('MNG', 'Mongolia', 'https://www.hltv.org/img/static/flags/30x20/MN.gif'),
('BGR', 'Bulgaria', 'https://www.hltv.org/img/static/flags/30x20/BG.gif'),
('SRB', 'Serbia', 'https://www.hltv.org/img/static/flags/30x20/RS.gif'),
('HRV', 'Croatia', 'https://www.hltv.org/img/static/flags/30x20/HR.gif'),
('SVN', 'Slovenia', 'https://www.hltv.org/img/static/flags/30x20/SI.gif'),
('LTU', 'Lithuania', 'https://www.hltv.org/img/static/flags/30x20/LT.gif'),
('LVA', 'Latvia', 'https://www.hltv.org/img/static/flags/30x20/LV.gif'),
('EST', 'Estonia', 'https://www.hltv.org/img/static/flags/30x20/EE.gif');

-- Игровые карты CS2 (актуальный пул карт)
INSERT INTO maps (name, display_name, image_url, is_active) VALUES
-- Active Duty карты
('de_dust2', 'Dust II', 'https://www.hltv.org/img/static/maps/de_dust2.png', true),
('de_mirage', 'Mirage', 'https://www.hltv.org/img/static/maps/de_mirage.png', true),
('de_inferno', 'Inferno', 'https://www.hltv.org/img/static/maps/de_inferno.png', true),
('de_nuke', 'Nuke', 'https://www.hltv.org/img/static/maps/de_nuke.png', true),
('de_overpass', 'Overpass', 'https://www.hltv.org/img/static/maps/de_overpass.png', true),
('de_vertigo', 'Vertigo', 'https://www.hltv.org/img/static/maps/de_vertigo.png', true),
('de_ancient', 'Ancient', 'https://www.hltv.org/img/static/maps/de_ancient.png', true),

-- Популярные карты, которые могут использоваться
('de_cache', 'Cache', 'https://www.hltv.org/img/static/maps/de_cache.png', false),
('de_train', 'Train', 'https://www.hltv.org/img/static/maps/de_train.png', false),
('de_cobblestone', 'Cobblestone', 'https://www.hltv.org/img/static/maps/de_cobblestone.png', false),
('de_tuscan', 'Tuscan', 'https://www.hltv.org/img/static/maps/de_tuscan.png', false),
('de_anubis', 'Anubis', 'https://www.hltv.org/img/static/maps/de_anubis.png', false);

-- Типы турниров/событий
INSERT INTO event_types (name, tier) VALUES
-- Tier S (Major турниры)
('Major Championship', 'S'),
('BLAST Premier: World Final', 'S'),
('IEM Katowice', 'S'),
('ESL Pro League Conference', 'S'),

-- Tier A (Премиум турниры)
('ESL Pro League', 'A'),
('BLAST Premier', 'A'),
('IEM Global Challenge', 'A'),
('PGL Major', 'A'),
('ELEAGUE Major', 'A'),
('DreamHack Masters', 'A'),
('StarSeries', 'A'),
('cs_summit', 'A'),

-- Tier B (Региональные турниры)
('ESL Challenger', 'B'),
('ESEA Advanced', 'B'),
('FPL-C', 'B'),
('Regional Championship', 'B'),
('Online Qualifier', 'B'),

-- Tier C (Локальные турниры)
('Local Tournament', 'C'),
('Community Cup', 'C'),
('Showmatch', 'C');

-- =====================================================
-- ПРИМЕРЫ КОМАНД (для демонстрации)
-- =====================================================

-- Получаем ID стран для команд
INSERT INTO teams (hltv_id, name, tag, country_id, world_ranking, points, hltv_url) VALUES
(4608, 'Natus Vincere', 'NAVI', (SELECT id FROM countries WHERE code = 'UKR'), 1, 1000, 'https://www.hltv.org/team/4608/natus-vincere'),
(9565, 'Team Vitality', 'VIT', (SELECT id FROM countries WHERE code = 'FRA'), 2, 950, 'https://www.hltv.org/team/9565/vitality'),
(6667, 'FaZe Clan', 'FaZe', (SELECT id FROM countries WHERE code = 'USA'), 3, 900, 'https://www.hltv.org/team/6667/faze'),
(5995, 'G2 Esports', 'G2', (SELECT id FROM countries WHERE code = 'FRA'), 4, 850, 'https://www.hltv.org/team/5995/g2'),
(5973, 'Team Liquid', 'TL', (SELECT id FROM countries WHERE code = 'USA'), 5, 800, 'https://www.hltv.org/team/5973/liquid'),
(6665, 'Astralis', 'AST', (SELECT id FROM countries WHERE code = 'DEN'), 6, 750, 'https://www.hltv.org/team/6665/astralis'),
(4991, 'Fnatic', 'FNC', (SELECT id FROM countries WHERE code = 'SWE'), 7, 700, 'https://www.hltv.org/team/4991/fnatic'),
(4494, 'MOUZ', 'MOUZ', (SELECT id FROM countries WHERE code = 'GER'), 8, 650, 'https://www.hltv.org/team/4494/mouz'),
(7532, 'BIG', 'BIG', (SELECT id FROM countries WHERE code = 'GER'), 9, 600, 'https://www.hltv.org/team/7532/big'),
(7175, 'Heroic', 'HER', (SELECT id FROM countries WHERE code = 'DEN'), 10, 550, 'https://www.hltv.org/team/7175/heroic');

-- =====================================================
-- ПРИМЕРЫ ИГРОКОВ (для демонстрации)
-- =====================================================

-- Игроки Natus Vincere
INSERT INTO players (hltv_id, nickname, real_name, country_id, age, hltv_url) VALUES
(7998, 's1mple', 'Oleksandr Kostyliev', (SELECT id FROM countries WHERE code = 'UKR'), 26, 'https://www.hltv.org/player/7998/s1mple'),
(11893, 'electronic', 'Denis Sharipov', (SELECT id FROM countries WHERE code = 'RUS'), 25, 'https://www.hltv.org/player/11893/electronic'),
(16555, 'Perfecto', 'Ilya Zalutskiy', (SELECT id FROM countries WHERE code = 'RUS'), 24, 'https://www.hltv.org/player/16555/perfecto'),
(18053, 'b1t', 'Valeriy Vakhovskiy', (SELECT id FROM countries WHERE code = 'UKR'), 22, 'https://www.hltv.org/player/18053/b1t'),
(1845, 'Boombl4', 'Kirill Mikhaylov', (SELECT id FROM countries WHERE code = 'RUS'), 25, 'https://www.hltv.org/player/1845/boombl4');

-- Игроки Team Vitality
INSERT INTO players (hltv_id, nickname, real_name, country_id, age, hltv_url) VALUES
(7322, 'ZywOo', 'Mathieu Herbaut', (SELECT id FROM countries WHERE code = 'FRA'), 23, 'https://www.hltv.org/player/7322/zywoo'),
(7169, 'apEX', 'Dan Madesclaire', (SELECT id FROM countries WHERE code = 'FRA'), 30, 'https://www.hltv.org/player/7169/apex'),
(8183, 'dupreeh', 'Peter Rasmussen', (SELECT id FROM countries WHERE code = 'DEN'), 30, 'https://www.hltv.org/player/8183/dupreeh'),
(9216, 'Magisk', 'Emil Reif', (SELECT id FROM countries WHERE code = 'DEN'), 25, 'https://www.hltv.org/player/9216/magisk'),
(429, 'Spinx', 'Lotan Giladi', (SELECT id FROM countries WHERE code = 'GBR'), 23, 'https://www.hltv.org/player/429/spinx');

-- =====================================================
-- СОСТАВЫ КОМАНД
-- =====================================================

-- Natus Vincere состав
INSERT INTO team_rosters (team_id, player_id, role, is_active) VALUES
((SELECT id FROM teams WHERE name = 'Natus Vincere'), (SELECT id FROM players WHERE nickname = 's1mple'), 'AWPer', true),
((SELECT id FROM teams WHERE name = 'Natus Vincere'), (SELECT id FROM players WHERE nickname = 'electronic'), 'Rifler', true),
((SELECT id FROM teams WHERE name = 'Natus Vincere'), (SELECT id FROM players WHERE nickname = 'Perfecto'), 'Support', true),
((SELECT id FROM teams WHERE name = 'Natus Vincere'), (SELECT id FROM players WHERE nickname = 'b1t'), 'Entry Fragger', true),
((SELECT id FROM teams WHERE name = 'Natus Vincere'), (SELECT id FROM players WHERE nickname = 'Boombl4'), 'IGL', true);

-- Team Vitality состав
INSERT INTO team_rosters (team_id, player_id, role, is_active) VALUES
((SELECT id FROM teams WHERE name = 'Team Vitality'), (SELECT id FROM players WHERE nickname = 'ZywOo'), 'AWPer', true),
((SELECT id FROM teams WHERE name = 'Team Vitality'), (SELECT id FROM players WHERE nickname = 'apEX'), 'IGL', true),
((SELECT id FROM teams WHERE name = 'Team Vitality'), (SELECT id FROM players WHERE nickname = 'dupreeh'), 'Support', true),
((SELECT id FROM teams WHERE name = 'Team Vitality'), (SELECT id FROM players WHERE nickname = 'Magisk'), 'Rifler', true),
((SELECT id FROM teams WHERE name = 'Team Vitality'), (SELECT id FROM players WHERE nickname = 'Spinx'), 'Entry Fragger', true);

-- =====================================================
-- ПРИМЕРЫ СТАТИСТИКИ ИГРОКОВ
-- =====================================================

-- Статистика s1mple за последние 3 месяца
INSERT INTO player_statistics (player_id, rating_2_0, kd_ratio, adr, kast, headshot_percentage, maps_played, kills_per_round, assists_per_round, deaths_per_round, period_start, period_end) VALUES
((SELECT id FROM players WHERE nickname = 's1mple'), 1.25, 1.32, 85.4, 72.5, 48.2, 45, 0.85, 0.12, 0.64, '2024-03-01', '2024-05-31');

-- Статистика ZywOo за последние 3 месяца
INSERT INTO player_statistics (player_id, rating_2_0, kd_ratio, adr, kast, headshot_percentage, maps_played, kills_per_round, assists_per_round, deaths_per_round, period_start, period_end) VALUES
((SELECT id FROM players WHERE nickname = 'ZywOo'), 1.28, 1.35, 87.1, 74.8, 51.3, 42, 0.88, 0.10, 0.65, '2024-03-01', '2024-05-31');

-- =====================================================
-- ПРИМЕР СОБЫТИЯ И МАТЧА
-- =====================================================

-- Создаем пример турнира
INSERT INTO events (hltv_id, name, event_type_id, start_date, end_date, prize_pool, location, hltv_url) VALUES
(7148, 'BLAST Premier Spring Final 2024', (SELECT id FROM event_types WHERE name = 'BLAST Premier'), '2024-06-01', '2024-06-09', 425000, 'London, UK', 'https://www.hltv.org/events/7148/blast-premier-spring-final-2024');

-- Создаем пример матча
INSERT INTO matches (hltv_id, event_id, team1_id, team2_id, match_format, match_type, scheduled_at, status, hltv_url) VALUES
(2370041, (SELECT id FROM events WHERE name = 'BLAST Premier Spring Final 2024'), 
 (SELECT id FROM teams WHERE name = 'Natus Vincere'), 
 (SELECT id FROM teams WHERE name = 'Team Vitality'), 
 'Bo3', 'Grand Final', '2024-06-09 16:00:00', 'scheduled', 'https://www.hltv.org/matches/2370041/natus-vincere-vs-vitality-blast-premier-spring-final-2024');

-- Создаем пример прогноза
INSERT INTO match_predictions (match_id, predicted_winner_id, confidence_percentage, predicted_score, prediction_text, reasoning, analyzed_factors) VALUES
((SELECT id FROM matches WHERE hltv_id = 2370041),
 (SELECT id FROM teams WHERE name = 'Team Vitality'),
 67.5,
 '2-1',
 'Team Vitality имеет преимущество в этом матче благодаря отличной форме ZywOo и стабильной игре команды в последние месяцы.',
 'Vitality показывает более консистентные результаты, ZywOo в отличной форме (рейтинг 1.28), команда хорошо играет на текущем мета-пуле карт.',
 '{"recent_form": {"vitality": "4-1", "navi": "3-2"}, "head_to_head": "2-1 в пользу Vitality", "key_players": {"zywoo_rating": 1.28, "s1mple_rating": 1.25}, "map_pool": "Vitality сильнее на Mirage и Inferno"}'::jsonb);

