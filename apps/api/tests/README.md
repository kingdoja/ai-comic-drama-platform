# Testing Infrastructure

This directory contains the test suite for the API application, including both unit tests and property-based tests.

## Setup

### Prerequisites

1. **Python 3.12+**: The project requires Python 3.12 or higher due to modern type hint syntax
2. **PostgreSQL Database**: A PostgreSQL instance must be running and accessible for database tests
3. **Python Dependencies**: Install test dependencies with `pip install -r requirements.txt`

### Database Setup

The tests use a separate test database to avoid affecting development data.

#### Option 1: Using Docker (Recommended)

```bash
# Start PostgreSQL using docker-compose
cd infra/docker
docker-compose up -d postgres
```

#### Option 2: Local PostgreSQL

If you have PostgreSQL installed locally, create the test database:

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE thinking_test;"

# Or using the provided Python script
cd apps/api
python tests/setup_test_db.py
```

### Environment Variables

You can override the test database URL by setting the `TEST_DATABASE_URL` environment variable:

```bash
export TEST_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/thinking_test"
```

## Running Tests

### Run All Tests

```bash
cd apps/api
pytest
```

### Run Specific Test Files

```bash
# Run unit tests only
pytest tests/unit/

# Run a specific test file
pytest tests/test_setup.py

# Run a specific test function
pytest tests/test_setup.py::test_database_fixture_works
```

### Run Property-Based Tests

Property-based tests use Hypothesis and are configured to run 100 iterations by default:

```bash
# Run with default profile (100 examples)
pytest tests/

# Run with dev profile (20 examples, faster)
HYPOTHESIS_PROFILE=dev pytest tests/

# Run with CI profile (200 examples, more thorough)
HYPOTHESIS_PROFILE=ci pytest tests/
```

### Verbose Output

```bash
# Show more details
pytest -v

# Show print statements
pytest -s

# Show both
pytest -vs
```

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── setup_test_db.py         # Script to create test database
├── test_setup.py            # Tests to verify setup works
├── unit/                    # Unit tests
│   ├── test_document_service.py
│   ├── test_review_service.py
│   └── test_text_workflow_service.py
└── property/                # Property-based tests (to be added)
```

## Fixtures

The following fixtures are available in all tests:

- `test_settings`: Test configuration with test database URL
- `test_engine`: SQLAlchemy engine for test database
- `test_session`: Database session with automatic rollback (test isolation)
- `db`: Alias for `test_session` for compatibility

### Example Usage

```python
def test_example(test_session):
    """Test using the database session."""
    project = ProjectModel(name="Test", source_mode="novel", target_platform="douyin")
    test_session.add(project)
    test_session.commit()
    
    result = test_session.query(ProjectModel).first()
    assert result.name == "Test"
```

## Hypothesis Configuration

Hypothesis profiles are configured in `conftest.py`:

- **default**: 100 examples, normal verbosity (for regular testing)
- **dev**: 20 examples, normal verbosity (for quick feedback during development)
- **ci**: 200 examples, verbose output (for CI/CD pipelines)

Select a profile using the `HYPOTHESIS_PROFILE` environment variable.

## Writing Tests

### Unit Tests

Unit tests should focus on specific behaviors and edge cases:

```python
def test_specific_behavior(test_session):
    """Test a specific behavior."""
    # Arrange
    # Act
    # Assert
```

### Property-Based Tests

Property-based tests verify universal properties across many inputs:

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_property(input_text):
    """Test a property that should hold for all inputs."""
    # Property assertion
    assert some_property_holds(input_text)
```

## Troubleshooting

### Database Connection Errors

If you see connection timeout errors:

1. Ensure PostgreSQL is running
2. Check the connection parameters in `apps/api/app/core/config.py`
3. Verify the test database exists: `python tests/setup_test_db.py`

### Test Isolation Issues

If tests are interfering with each other:

1. Ensure you're using the `test_session` fixture (not creating your own sessions)
2. The fixture automatically rolls back transactions after each test
3. Check that you're not committing outside the test session

### Hypothesis Failures

If a property-based test fails:

1. Hypothesis will show you the failing example
2. You can reproduce the failure by running the test again
3. Use `@example(...)` decorator to add the failing case as a regression test
