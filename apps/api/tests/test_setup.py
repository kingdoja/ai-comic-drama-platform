"""
Test to verify pytest and Hypothesis setup.

This test ensures that:
1. Pytest is configured correctly
2. Database fixtures work
3. Hypothesis is installed and configured
"""

import uuid
from datetime import datetime

import pytest
from hypothesis import given, strategies as st
from sqlalchemy.orm import Session

from app.db.models import ProjectModel


def test_database_fixture_works(test_session: Session):
    """Test that database session fixture works correctly."""
    # Create a test project
    project = ProjectModel(
        id=uuid.uuid4(),
        name="Test Project",
        source_mode="novel",
        target_platform="douyin",
        status="draft"
    )
    
    test_session.add(project)
    test_session.commit()
    
    # Query it back
    retrieved = test_session.query(ProjectModel).filter_by(name="Test Project").first()
    
    assert retrieved is not None
    assert retrieved.name == "Test Project"
    assert retrieved.source_mode == "novel"
    assert retrieved.target_platform == "douyin"


def test_database_isolation(test_session: Session):
    """Test that each test gets a clean database state."""
    # This test should not see any data from previous tests
    count = test_session.query(ProjectModel).count()
    assert count == 0, "Database should be empty at start of test"


@given(st.text(min_size=1, max_size=100))
def test_hypothesis_works(project_name: str):
    """Test that Hypothesis property-based testing works."""
    # Simple property: non-empty strings should have positive length
    assert len(project_name) > 0
    assert len(project_name) <= 100


@given(
    st.integers(min_value=1, max_value=100),
    st.integers(min_value=1, max_value=100)
)
def test_hypothesis_with_multiple_inputs(a: int, b: int):
    """Test Hypothesis with multiple generated inputs."""
    # Property: addition is commutative
    assert a + b == b + a
    
    # Property: both inputs are positive
    assert a > 0
    assert b > 0


def test_db_alias_fixture_works(db: Session):
    """Test that 'db' alias fixture works."""
    # Create a test project using 'db' instead of 'test_session'
    project = ProjectModel(
        id=uuid.uuid4(),
        name="Test with db alias",
        source_mode="script",
        target_platform="kuaishou",
        status="draft"
    )
    
    db.add(project)
    db.commit()
    
    # Query it back
    retrieved = db.query(ProjectModel).filter_by(name="Test with db alias").first()
    
    assert retrieved is not None
    assert retrieved.name == "Test with db alias"
