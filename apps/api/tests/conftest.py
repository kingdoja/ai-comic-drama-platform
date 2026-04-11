"""
Pytest configuration and fixtures for testing.

Provides database fixtures for both unit and property-based tests:
- test_engine: SQLAlchemy engine for test database
- test_session: Database session for tests
- db: Alias for test_session for compatibility
"""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base
from app.core.config import Settings


# Override settings for testing
@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings with test database URL."""
    # Use a separate test database
    test_db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/thinking_test"
    )
    
    settings = Settings()
    settings.database_url = test_db_url
    return settings


@pytest.fixture(scope="session")
def test_engine(test_settings: Settings) -> Generator[Engine, None, None]:
    """
    Create a test database engine.
    
    This fixture:
    1. Creates a new database engine for testing
    2. Creates all tables before tests
    3. Drops all tables after tests
    """
    engine = create_engine(test_settings.database_url, future=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine: Engine) -> Generator[Session, None, None]:
    """
    Create a test database session with transaction rollback.
    
    This fixture:
    1. Creates a new connection and transaction
    2. Creates a session bound to the transaction
    3. Rolls back the transaction after each test (cleanup)
    
    This ensures test isolation - each test starts with a clean database state.
    """
    # Create a connection
    connection = test_engine.connect()
    
    # Begin a transaction
    transaction = connection.begin()
    
    # Create a session bound to the connection
    TestSessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False, future=True)
    session = TestSessionLocal()
    
    yield session
    
    # Rollback the transaction (cleanup)
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def db(test_session: Session) -> Session:
    """
    Alias for test_session for compatibility with existing code.
    
    This allows tests to use either 'test_session' or 'db' as the fixture name.
    """
    return test_session


# Test data fixtures
from uuid import uuid4
from app.db.models import ProjectModel, EpisodeModel


@pytest.fixture(scope="function")
def test_project(test_session: Session) -> ProjectModel:
    """Create a test project."""
    project = ProjectModel(
        id=uuid4(),
        name="Test Project",
        source_mode="original",
        target_platform="web",
        status="active"
    )
    test_session.add(project)
    test_session.flush()
    return project


@pytest.fixture(scope="function")
def test_episode(test_session: Session, test_project: ProjectModel) -> EpisodeModel:
    """Create a test episode."""
    episode = EpisodeModel(
        id=uuid4(),
        project_id=test_project.id,
        episode_no=1,
        title="Test Episode",
        target_duration_sec=300  # 5 minutes
    )
    test_session.add(episode)
    test_session.flush()
    return episode


# Configure Hypothesis settings for property-based tests
from hypothesis import settings as hypothesis_settings, Verbosity

# Register a profile for property-based tests
hypothesis_settings.register_profile(
    "default",
    max_examples=100,  # Run 100 iterations per property test
    verbosity=Verbosity.normal,
    deadline=None,  # Disable deadline for database operations
)

# Register a profile for CI/CD with more examples
hypothesis_settings.register_profile(
    "ci",
    max_examples=200,
    verbosity=Verbosity.verbose,
    deadline=None,
)

# Register a profile for quick testing during development
hypothesis_settings.register_profile(
    "dev",
    max_examples=20,
    verbosity=Verbosity.normal,
    deadline=None,
)

# Load the profile from environment variable or use default
hypothesis_settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))
