"""
Script to create test database if it doesn't exist.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError


def create_test_database():
    """Create the test database if it doesn't exist."""
    # Connect to the default postgres database
    engine = create_engine('postgresql+psycopg://postgres:postgres@localhost:5432/postgres')
    
    # Check if test database exists
    with engine.connect() as conn:
        # Need to commit to execute outside transaction
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'thinking_test'"))
        exists = result.fetchone()
        
        if not exists:
            print("Creating test database 'thinking_test'...")
            conn.execute(text("CREATE DATABASE thinking_test"))
            print("Test database created successfully!")
        else:
            print("Test database 'thinking_test' already exists.")
    
    engine.dispose()


if __name__ == "__main__":
    try:
        create_test_database()
    except Exception as e:
        print(f"Error creating test database: {e}")
        print("Please ensure PostgreSQL is running and accessible.")
        exit(1)
