from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .utils.logger import setup_logger
import os
from datetime import datetime

logger = setup_logger(__name__)

# Keep the existing logic
DB_DIRECTORY = os.getenv('DB_DIRECTORY', './data4c')
DB_FILENAME = 'db4chatbot.db'
DB_PATH = os.path.join(DB_DIRECTORY, DB_FILENAME)

# Similarly for other paths
MODEL_DIRECTORY = os.getenv('MODEL_DIRECTORY', './data4c/results')
MODEL_FILENAME = 'model_distill_bert.pth'
MODEL_PATH = os.path.join(MODEL_DIRECTORY, MODEL_FILENAME)

TRAINING_DATA_DIRECTORY = os.getenv('TRAINING_DATA_DIRECTORY', './data4c')
TRAINING_DATA_FILENAME = 'customer_queries.csv'
TRAINING_DATA_PATH = os.path.join(TRAINING_DATA_DIRECTORY, TRAINING_DATA_FILENAME)

# Ensure data directory exists
os.makedirs(DB_DIRECTORY, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database if it doesn't exist"""
    from . import models  # Import models here to avoid circular imports
    
    if os.path.exists(DB_PATH):
        logger.info(f"Database already exists at {DB_PATH}")
        return False
        
    try:
        # Create backup directory
        backup_dir = os.path.join(DB_DIRECTORY, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create tables
        logger.info("Creating new database...")
        Base.metadata.create_all(bind=engine)
        
        # Create a session
        db = SessionLocal()
        try:
            # Create a default admin user
            admin_user = models.User(
                email="admin@example.com",
                password="admin123",
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            logger.debug("Added admin user")
            
            # Create a default regular user
            regular_user = models.User(
                email="user@example.com",
                password="user123",
                is_active=True,
                is_superuser=False
            )
            db.add(regular_user)
            logger.debug("Added regular user")
            
            db.commit()
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating default users: {e}", exc_info=True)
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise

def backup_db():
    """Create a backup of the database"""
    if not os.path.exists(DB_PATH):
        logger.warning("No database to backup")
        return
        
    try:
        # Create backup directory
        backup_dir = os.path.join(DB_DIRECTORY, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'db4chatbot_{timestamp}.db')
        
        # Copy current database to backup
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        logger.info(f"Database backed up to {backup_path}")
        
        # Keep only last 5 backups
        backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('db4chatbot_')])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(os.path.join(backup_dir, old_backup))
                logger.debug(f"Removed old backup: {old_backup}")
                
    except Exception as e:
        logger.error(f"Error backing up database: {e}", exc_info=True)