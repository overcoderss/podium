import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import database
import main

Base = database.Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

main.app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(main.app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_and_login():
    # Register
    response = client.post(
        "/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123", "full_name": "Test User", "role": "team"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Login
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    token = response.json()["access_token"]

    # Get Me
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_create_tournament_as_admin():
    # Register admin
    client.post(
        "/register",
        json={"username": "admin", "email": "admin@example.com", "password": "adminpassword", "full_name": "Admin User", "role": "admin"},
    )
    login_resp = client.post(
        "/login",
        json={"username": "admin", "password": "adminpassword"},
    )
    token = login_resp.json()["access_token"]

    # Create tournament
    tournament_data = {
        "title": "Test Tournament",
        "description": "Desc",
        "reg_start": "2026-05-01T00:00:00",
        "reg_end": "2026-05-31T23:59:59",
        "min_team_size": 2,
        "max_team_size": 5,
        "is_public": True
    }
    response = client.post(
        "/tournaments",
        json=tournament_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Tournament"
