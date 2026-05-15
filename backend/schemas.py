from pydantic import BaseModel, ConfigDict, HttpUrl
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class TeamMemberBase(BaseModel):
    full_name: str
    email: str

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberResponse(TeamMemberBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class TeamBase(BaseModel):
    name: str
    school_info: Optional[str] = None

class TeamCreate(TeamBase):
    members: List[TeamMemberCreate]

class TeamResponse(TeamBase):
    id: int
    tournament_id: int
    captain_id: int
    members: List[TeamMemberResponse]

    model_config = ConfigDict(from_attributes=True)

class TournamentBase(BaseModel):
    title: str
    description: str
    reg_start: Optional[datetime] = None
    reg_end: Optional[datetime] = None
    min_team_size: int = 2
    max_team_size: int = 5
    is_public: bool = True

class TournamentCreate(TournamentBase):
    pass

class TournamentResponse(TournamentBase):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)

class TaskBase(BaseModel):
    title: str
    description: str
    deadline: datetime
    must_have_criteria: str

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    tournament_id: int
    status: Optional[str] = None

    class Config:
        from_attributes = True

class SubmissionBase(BaseModel):
    github_url: HttpUrl
    video_url: Optional[HttpUrl] = None
    live_demo_url: Optional[HttpUrl] = None
    description: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionResponse(SubmissionBase):
    id: int
    team_id: int
    submitted_at: datetime

    class Config:
        from_attributes = True

class GradeBase(BaseModel):
    tech_score: float
    functional_score: float
    comments: Optional[str] = None

class GradeCreate(GradeBase):
    submission_id: int

class GradeResponse(GradeBase):
    id: int
    submission_id: int
    jury_id: int

    model_config = ConfigDict(from_attributes=True)
