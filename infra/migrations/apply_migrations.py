"""
Apply SQL migrations to the database.

This script reads all .sql files in the migrations directory and applies them in order.
"""
import psycopg
from pathlib import Path
import sys

def apply_migrations():
    """Apply all SQL migrations in order."""
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'postgres',
        'dbname': 'thinking'
    }
    
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg.connect(**db_params, autocommit=True)
        cursor = conn.cursor()
        
        # Get migrations directory
        migrations_dir = Path(__file__).parent
        migration_files = sorted(migrations_dir.glob('*.sql'))
        
        if not migration_files:
            print("No migration files found!")
            return
        
        print(f"Found {len(migration_files)} migration files\n")
        
        # Apply each migration
        for migration_file in migration_files:
            print(f"Applying {migration_file.name}...")
            
            try:
                sql = migration_file.read_text(encoding='utf-8')
                cursor.execute(sql)
                print(f"✓ {migration_file.name} applied successfully\n")
            except Exception as e:
                print(f"✗ Error applying {migration_file.name}: {e}\n")
                # Continue with next migration
        
        cursor.close()
        conn.close()
        print("All migrations completed!")
        
    except psycopg.OperationalError as e:
        print(f"Failed to connect to database: {e}")
        print("\nMake sure:")
        print("1. Docker PostgreSQL is running: docker-compose up -d postgres")
        print("2. Database connection parameters are correct")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    apply_migrations()
