"""
Database models and connection setup for HLTV Parser
"""

import os
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Date, DECIMAL, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

Base = declarative_base()

# Настройки подключения к БД
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'ai_betting')}"
)

# Создаем движок и сессию
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    hltv_id = Column(Integer, unique=True, nullable=False, comment="ID команды на HLTV.org")
    name = Column(String(100), nullable=False, comment="Название команды")
    tag = Column(String(10), nullable=True, comment="Короткий тег (NAVI, G2)")
    country_code = Column(String(3), nullable=True, comment="Код страны")
    country_name = Column(String(100), nullable=True, comment="Название страны")
    logo_url = Column(String(255), nullable=True, comment="URL логотипа")
    hltv_url = Column(String(255), nullable=True, comment="Ссылка на HLTV")
    world_ranking = Column(Integer, nullable=True, comment="Мировой рейтинг")
    points = Column(Integer, default=0, comment="Рейтинговые очки")
    is_active = Column(Boolean, default=True, comment="Активна ли команда")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    rosters = relationship("TeamRoster", back_populates="team")
    matches_as_team1 = relationship("Match", foreign_keys="Match.team1_id", back_populates="team1")
    matches_as_team2 = relationship("Match", foreign_keys="Match.team2_id", back_populates="team2")
    
    # Indexes
    __table_args__ = (
        Index('idx_teams_hltv_id', 'hltv_id'),
        Index('idx_teams_world_ranking', 'world_ranking'),
        Index('idx_teams_is_active', 'is_active'),
    )


class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    hltv_id = Column(Integer, unique=True, nullable=False, comment="ID игрока на HLTV.org")
    nickname = Column(String(50), nullable=False, comment="Игровой ник")
    real_name = Column(String(100), nullable=True, comment="Настоящее имя")
    country_code = Column(String(3), nullable=True, comment="Код страны")
    country_name = Column(String(100), nullable=True, comment="Название страны")
    age = Column(Integer, nullable=True, comment="Возраст с проверкой")
    avatar_url = Column(String(255), nullable=True, comment="URL аватара")
    hltv_url = Column(String(255), nullable=True, comment="Ссылка на HLTV")
    is_active = Column(Boolean, default=True, comment="Активен ли игрок")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    rosters = relationship("TeamRoster", back_populates="player")
    statistics = relationship("PlayerStatistics", back_populates="player")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('age > 0 AND age < 100', name='chk_players_age'),
        Index('idx_players_hltv_id', 'hltv_id'),
        Index('idx_players_is_active', 'is_active'),
    )


class TeamRoster(Base):
    __tablename__ = "team_rosters"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=True, comment="Роль (IGL, AWPer, Support)")
    is_active = Column(Boolean, default=True, comment="Активен ли в составе")
    joined_at = Column(DateTime, nullable=False, comment="Дата присоединения")
    left_at = Column(DateTime, nullable=True, comment="Дата ухода (NULL если активен)")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="rosters")
    player = relationship("Player", back_populates="rosters")


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    hltv_id = Column(Integer, unique=True, nullable=False, comment="ID события на HLTV.org")
    name = Column(String(200), nullable=False, comment="Название турнира")
    event_type = Column(String(50), nullable=True, comment="Тип турнира")
    tier = Column(String(20), nullable=True, comment="Уровень турнира (S, A, B, C)")
    start_date = Column(Date, nullable=False, comment="Дата начала")
    end_date = Column(Date, nullable=False, comment="Дата окончания")
    prize_pool = Column(Integer, nullable=True, comment="Призовой фонд в USD")
    location = Column(String(100), nullable=True, comment="Место проведения")
    hltv_url = Column(String(255), nullable=True, comment="Ссылка на HLTV")
    is_completed = Column(Boolean, default=False, comment="Завершен ли турнир")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    matches = relationship("Match", back_populates="event")


class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    hltv_id = Column(Integer, unique=True, nullable=False, comment="ID матча на HLTV.org")
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=True)
    event_name = Column(String(200), nullable=True, comment="Название события")
    team1_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    team2_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    team1_score = Column(Integer, nullable=True, comment="Счет первой команды")
    team2_score = Column(Integer, nullable=True, comment="Счет второй команды")
    winner_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    match_format = Column(String(20), nullable=False, comment="Bo1, Bo3, Bo5")
    match_type = Column(String(50), nullable=True, comment="Group Stage, Final и т.д.")
    scheduled_at = Column(DateTime, nullable=True, comment="Запланированное время")
    started_at = Column(DateTime, nullable=True, comment="Время начала")
    ended_at = Column(DateTime, nullable=True, comment="Время окончания")
    status = Column(String(20), default='scheduled', comment="scheduled, live, completed, cancelled")
    hltv_url = Column(String(255), nullable=True, comment="Ссылка на HLTV")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="matches")
    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="matches_as_team1")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="matches_as_team2")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('team1_id != team2_id', name='chk_matches_different_teams'),
        Index('idx_matches_scheduled_at', 'scheduled_at'),
        Index('idx_matches_status', 'status'),
        Index('idx_matches_teams', 'team1_id', 'team2_id'),
    )


class PlayerStatistics(Base):
    __tablename__ = "player_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    rating_2_0 = Column(DECIMAL(4, 3), nullable=True, comment="Рейтинг 2.0 (1.234)")
    kd_ratio = Column(DECIMAL(4, 3), nullable=True, comment="Kill/Death ratio")
    adr = Column(DECIMAL(5, 2), nullable=True, comment="Average Damage per Round")
    kast = Column(DECIMAL(5, 2), nullable=True, comment="KAST percentage")
    headshot_percentage = Column(DECIMAL(5, 2), nullable=True, comment="Процент хедшотов")
    maps_played = Column(Integer, default=0, comment="Количество сыгранных карт")
    kills_per_round = Column(DECIMAL(4, 3), nullable=True, comment="Убийств за раунд")
    assists_per_round = Column(DECIMAL(4, 3), nullable=True, comment="Ассистов за раунд")
    deaths_per_round = Column(DECIMAL(4, 3), nullable=True, comment="Смертей за раунд")
    saved_by_teammate_per_round = Column(DECIMAL(4, 3), nullable=True, comment="Спасений командой")
    saved_teammates_per_round = Column(DECIMAL(4, 3), nullable=True, comment="Спасений команды")
    period_start = Column(Date, nullable=False, comment="Начало периода")
    period_end = Column(Date, nullable=False, comment="Конец периода")
    last_updated = Column(DateTime, nullable=True, comment="Последнее обновление")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="statistics")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('rating_2_0 >= 0 AND rating_2_0 <= 3', name='chk_rating_range'),
        CheckConstraint('kd_ratio >= 0', name='chk_kd_positive'),
        CheckConstraint('adr >= 0', name='chk_adr_positive'),
        CheckConstraint('kast >= 0 AND kast <= 100', name='chk_kast_percentage'),
        CheckConstraint('headshot_percentage >= 0 AND headshot_percentage <= 100', name='chk_hs_percentage'),
        CheckConstraint('maps_played >= 0', name='chk_maps_positive'),
        Index('idx_player_stats_player_id', 'player_id'),
        Index('idx_player_stats_period', 'period_start', 'period_end'),
    )


def get_db() -> Session:
    """
    Получить сессию базы данных
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def create_or_get_event(db: Session, name: str, event_type: str = "Tournament") -> Event:
    """
    Создать или получить существующее событие
    """
    existing_event = db.query(Event).filter(Event.name == name).first()
    if existing_event:
        return existing_event
    
    new_event = Event(
        hltv_id=0,  # Будет обновлено при получении полной информации
        name=name,
        event_type=event_type,
        tier="A",
        start_date=datetime.now().date(),
        end_date=datetime.now().date()
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event 