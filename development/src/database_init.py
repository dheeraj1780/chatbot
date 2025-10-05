"""
Database initialization script
Run this to create tables and initial admin user
"""
import asyncio
import bcrypt
from utils.db_connection import DatabaseConnection
from repository.orm import UserRepository
from utils.db_connection import get_db_session

async def create_admin_user():
    """Create initial admin user"""
    async with get_db_session() as session:
        user_repo = UserRepository(session)
        
        # Check if admin already exists
        existing_admin = await user_repo.get_user_by_username("admin")
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        password = "admin"  # Change this!
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        admin_user = await user_repo.create_user(
            username="admin",
            password_hash=password_hash,
            role="admin"
        )
        
        print(f"Admin user created: {admin_user.username}")
        print(f"Default password: {password}")
        print("Please change the password after first login!")

async def initialize_database():
    """Initialize database with tables and admin user"""
    try:
        db = DatabaseConnection()
        
        # Create tables
        print("Creating database tables...")
        await db.create_tables()
        print("Tables created successfully!")
        
        # Create admin user
        print("Creating admin user...")
        await create_admin_user()
        print("Database initialization complete!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(initialize_database())