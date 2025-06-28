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
    f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'cs2_predictions')}"
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
    hltv_url = Column(String(255), nullable=True, comment="Ссылка на HLTV")
    is_active = Column(Boolean, default=True, comment="Активен ли игрок")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    rosters = relationship("TeamRoster", back_populates="player")
    statistics = relationship("PlayerStatistics", back_populates="player")
    
    # Constraints
    __table_args__ = (
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


class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    hltv_id = Column(Integer, unique=True, nullable=False, comment="ID матча на HLTV.org")
    team1_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    team2_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    team1_score = Column(Integer, nullable=True, comment="Счет первой команды")
    team2_score = Column(Integer, nullable=True, comment="Счет второй команды")
    winner_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    match_format = Column(String(20), nullable=False, comment="Bo1, Bo3, Bo5")
    scheduled_at = Column(DateTime, nullable=True, comment="Запланированное время")
    started_at = Column(DateTime, nullable=True, comment="Время начала")
    ended_at = Column(DateTime, nullable=True, comment="Время окончания")
    status = Column(String(20), default='scheduled', comment="scheduled, live, completed, cancelled")
    hltv_url = Column(String(255), nullable=True, comment="Ссылка на HLTV")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
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
    kills_per_round = Column(DECIMAL(4, 3), nullable=True, comment="Убийств за раунд")
    assists_per_round = Column(DECIMAL(4, 3), nullable=True, comment="Ассистов за раунд")
    deaths_per_round = Column(DECIMAL(4, 3), nullable=True, comment="Смертей за раунд")
    period_start = Column(Date, nullable=False, comment="Начало периода")
    period_end = Column(Date, nullable=False, comment="Конец периода")
    last_updated = Column(DateTime, nullable=True, comment="Последнее обновление")
    maps_played = Column(Integer, default=0, comment="Количество сыгранных карт")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="statistics")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('rating_2_0 >= 0 AND rating_2_0 <= 3', name='chk_rating_range'),
        CheckConstraint('kd_ratio >= 0', name='chk_kd_positive'),
        CheckConstraint('adr >= 0', name='chk_adr_positive'),
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


def get_team_by_name(db: Session, team_name: str) -> Optional[Team]:
    """
    Найти команду по ее точному названию.
    """
    return db.query(Team).filter(Team.name == team_name).first() 