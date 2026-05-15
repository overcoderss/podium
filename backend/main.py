from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import random

import models
import schemas
import auth
import database
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Podium API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Endpoints
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "username": user.username}

@app.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# Tournament Endpoints
@app.post("/tournaments", response_model=schemas.TournamentResponse)
def create_tournament(
    tournament: schemas.TournamentCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.check_admin)
):
    db_tournament = models.Tournament(**tournament.model_dump())
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament

@app.get("/tournaments", response_model=List[schemas.TournamentResponse])
def list_tournaments(db: Session = Depends(get_db)):
    return db.query(models.Tournament).all()

@app.get("/tournaments/{tournament_id}", response_model=schemas.TournamentResponse)
def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament

@app.patch("/tournaments/{tournament_id}/status", response_model=schemas.TournamentResponse)
def update_tournament_status(
    tournament_id: int,
    status: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.check_admin)
):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament.status = status
    db.commit()
    db.refresh(tournament)
    return tournament

# Team Registration
@app.post("/tournaments/{tournament_id}/register-team", response_model=schemas.TeamResponse)
def register_team(
    tournament_id: int,
    team_data: schemas.TeamCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.check_team)
):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    if tournament.status != "registration":
        raise HTTPException(status_code=400, detail="Registration is not open for this tournament")
    if tournament.reg_start and datetime.utcnow() < tournament.reg_start:
        raise HTTPException(status_code=400, detail="Registration has not started yet")
    if tournament.reg_end and datetime.utcnow() > tournament.reg_end:
        raise HTTPException(status_code=400, detail="Registration has closed")

    if len(team_data.members) < tournament.min_team_size or len(team_data.members) > tournament.max_team_size:
        raise HTTPException(status_code=400, detail="Team size is outside allowed limits")

    emails = [m.email for m in team_data.members]
    if len(emails) != len(set(emails)):
        raise HTTPException(status_code=400, detail="Emails within the team must be unique")

    if db.query(models.Team).filter(models.Team.name == team_data.name).first():
        raise HTTPException(status_code=400, detail="Team name already taken")

    existing_team = db.query(models.Team).filter(
        models.Team.tournament_id == tournament_id,
        models.Team.captain_id == current_user.id
    ).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="You are already a captain of a team in this tournament")

    new_team = models.Team(
        name=team_data.name,
        tournament_id=tournament_id,
        captain_id=current_user.id,
        school_info=team_data.school_info,
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    for member in team_data.members:
        db_member = models.TeamMember(
            team_id=new_team.id,
            full_name=member.full_name,
            email=member.email
        )
        db.add(db_member)

    db.commit()
    db.refresh(new_team)
    return new_team

# Task Endpoints
@app.post("/tournaments/{tournament_id}/tasks", response_model=schemas.TaskResponse)
def create_task(
    tournament_id: int,
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.check_admin)
):
    db_task = models.Task(**task.dict(), tournament_id=tournament_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.patch("/tasks/{task_id}/status", response_model=schemas.TaskResponse)
def update_task_status(
    task_id: int,
    status: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.check_admin)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = status
    db.commit()
    db.refresh(task)
    return task

# Submission Endpoints
@app.post("/tasks/{task_id}/submit", response_model=schemas.SubmissionResponse)
def submit_task(
    task_id: int,
    submission: schemas.SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.check_team)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "active":
        raise HTTPException(status_code=400, detail="Submissions are not open for this task")
    if task.deadline and datetime.utcnow() > task.deadline:
        task.status = "submission_closed"
        db.commit()
        raise HTTPException(status_code=400, detail="Deadline has passed")

    team = db.query(models.Team).filter(
        models.Team.tournament_id == task.tournament_id,
        models.Team.captain_id == current_user.id
    ).first()
    if not team:
        raise HTTPException(status_code=403, detail="Only captains can submit for the team")

    existing_sub = db.query(models.Submission).filter(
        models.Submission.task_id == task_id,
        models.Submission.team_id == team.id
    ).first()

    if existing_sub:
        existing_sub.github_url = submission.github_url
        existing_sub.video_url = submission.video_url
        existing_sub.live_demo_url = submission.live_demo_url
        existing_sub.description = submission.description
        existing_sub.submitted_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_sub)
        return existing_sub

    new_submission = models.Submission(
        task_id=task_id,
        team_id=team.id,
        github_url=submission.github_url,
        video_url=submission.video_url,
        live_demo_url=submission.live_demo_url,
        description=submission.description,
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    return new_submission

# Jury Endpoints
@app.post("/tasks/{task_id}/assign-jury")
def assign_jury(
    task_id: int,
    k: int = 2,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.check_admin)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    submissions = db.query(models.Submission).filter(models.Submission.task_id == task_id).all()
    if not submissions:
        raise HTTPException(status_code=400, detail="No submissions to assign")
    
    juries = db.query(models.User).filter(models.User.role == "jury").all()
    if len(juries) < k:
        raise HTTPException(status_code=400, detail=f"Not enough jury members (need at least {k})")

    for sub in submissions:
        assigned_juries = random.sample(juries, k)
        for jury in assigned_juries:
            existing_grade = db.query(models.Grade).filter(
                models.Grade.submission_id == sub.id,
                models.Grade.jury_id == jury.id
            ).first()
            if not existing_grade:
                new_grade = models.Grade(
                    submission_id=sub.id,
                    jury_id=jury.id,
                    tech_score=0.0,
                    functional_score=0.0
                )
                db.add(new_grade)

            existing_grade = db.query(models.Grade).filter(
                models.Grade.submission_id == sub.id,
                models.Grade.jury_id == jury.id
            ).first()
            if not existing_grade:
                new_grade = models.Grade(
                    submission_id=sub.id,
                    jury_id=jury.id,
                    tech_score=0.0,
                    functional_score=0.0
                )
                db.add(new_grade)
    
    db.commit()
    return {"message": f"Successfully assigned {k} jury members to {len(submissions)} submissions"}

@app.get("/jury/assignments", response_model=List[schemas.SubmissionResponse])
def get_jury_assignments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.check_jury)
):
    # Find all submissions where this jury is assigned (via Grades table)
    grades = db.query(models.Grade).filter(models.Grade.jury_id == current_user.id).all()
    submission_ids = [g.submission_id for g in grades]
    return db.query(models.Submission).filter(models.Submission.id.in_(submission_ids)).all()

@app.post("/submissions/{submission_id}/grade", response_model=schemas.GradeResponse)
def grade_submission(
    submission_id: int,
    grade: schemas.GradeBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.check_jury)
):
    db_grade = db.query(models.Grade).filter(
        models.Grade.submission_id == submission_id,
        models.Grade.jury_id == current_user.id
    ).first()
    if not db_grade:
        raise HTTPException(status_code=403, detail="You are not assigned to this submission")

    db_grade.tech_score = grade.tech_score
    db_grade.functional_score = grade.functional_score
    db_grade.comments = grade.comments

    db.commit()
    db.refresh(db_grade)
    return db_grade

# Leaderboard Endpoint
@app.get("/tournaments/{tournament_id}/leaderboard")
def get_leaderboard(tournament_id: int, db: Session = Depends(get_db)):
    teams = db.query(models.Team).filter(models.Team.tournament_id == tournament_id).all()
    leaderboard = []
    
    for team in teams:
        # Get all submissions for this team in this tournament
        submissions = db.query(models.Submission).join(models.Task).filter(
            models.Submission.team_id == team.id,
            models.Task.tournament_id == tournament_id
        ).all()
        
        total_score = 0.0
        details = []
        for sub in submissions:
            # Average scores from all juries for this submission
            grades = db.query(models.Grade).filter(models.Grade.submission_id == sub.id).all()
            if grades:
                sub_score = sum((g.tech_score + g.functional_score) / 2 for g in grades) / len(grades)
                total_score += sub_score
                details.append({
                    "task_id": sub.task_id,
                    "score": sub_score
                })
        
        leaderboard.append({
            "team_id": team.id,
            "team_name": team.name,
            "total_score": round(total_score, 2),
            "details": details
        })
    
    leaderboard.sort(key=lambda x: x["total_score"], reverse=True)
    return leaderboard
