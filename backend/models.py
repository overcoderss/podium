from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    JURY = "jury"
    TEAM = "team"

class TournamentStatus(str, enum.Enum):
    DRAFT = "draft"
    REGISTRATION = "registration"
    RUNNING = "running"
    FINISHED = "finished"

class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    teams_captain = relationship("Team", back_populates="captain")
    grades_given = relationship("Grade", back_populates="jury")

class UserSession(Base):
    __tablename__ = "User_Sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String, unique=True, index=True, nullable=False)
    ip_address = Column(String, nullable=True)
    device_info = Column(String, nullable=True)
    last_active = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="sessions")

class Tournament(Base):
    __tablename__ = "Tournaments"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="draft")
    reg_start = Column(DateTime(timezone=True))
    reg_end = Column(DateTime(timezone=True))
    min_team_size = Column(Integer, default=2)
    max_team_size = Column(Integer, default=5)
    is_public = Column(Boolean, default=True)

    teams = relationship("Team", back_populates="tournament")
    tasks = relationship("Task", back_populates="tournament")

class Team(Base):
    __tablename__ = "Teams"
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("Tournaments.id"), nullable=False)
    name = Column(String, unique=True, nullable=False)
    captain_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    school_info = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tournament = relationship("Tournament", back_populates="teams")
    captain = relationship("User", back_populates="teams_captain")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="team")

class TeamMember(Base):
    __tablename__ = "Team_Members"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("Teams.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)

    team = relationship("Team", back_populates="members")

class Task(Base):
    __tablename__ = "Tasks"
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("Tournaments.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    deadline = Column(DateTime(timezone=True))
    must_have_criteria = Column(Text)
    status = Column(String, default="active")

    tournament = relationship("Tournament", back_populates="tasks")
    submissions = relationship("Submission", back_populates="task")

class Submission(Base):
    __tablename__ = "Submissions"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("Tasks.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("Teams.id"), nullable=False)
    github_url = Column(String)
    video_url = Column(String)
    live_demo_url = Column(String)
    description = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("Task", back_populates="submissions")
    team = relationship("Team", back_populates="submissions")
    grades = relationship("Grade", back_populates="submission", cascade="all, delete-orphan")

class Grade(Base):
    __tablename__ = "Grades"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("Submissions.id", ondelete="CASCADE"), nullable=False)
    jury_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    tech_score = Column(Float, default=0.0)
    functional_score = Column(Float, default=0.0)
    comments = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    submission = relationship("Submission", back_populates="grades")
    jury = relationship("User", back_populates="grades_given")
