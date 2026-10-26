"""Shared pytest fixtures for the test suite.

Each test gets a fresh, isolated SQLite database file and a TestClient
wired up to use that database instead of the app's default one.
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app, get_db

TEST_DATABASE_URL = "sqlite:///./test_expenses.db"


@pytest.fixture()
def client():
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_expenses.db"):
        os.remove("./test_expenses.db")
