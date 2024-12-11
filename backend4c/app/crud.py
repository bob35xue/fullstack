from sqlalchemy.orm import Session
from . import models
from datetime import datetime
from .utils.logger import setup_logger

logger = setup_logger(__name__)

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if user.password != password:  # Simple password comparison
        return None
    return user

def create_user(db: Session, email: str, password: str, is_active: bool = True, is_superuser: bool = False):
    db_user = models.User(
        email=email,
        password=password,  # Store plain password
        is_active=is_active,
        is_superuser=is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_issues(db: Session, user_id: int):
    return db.query(models.Issue).filter(models.Issue.user_id == user_id).all()

def create_user_issue(
    db: Session, 
    issue: models.IssueCreate, 
    user_id: int,
    product_code: int,
    product_name: str,
    response: str
):
    # Get current time in local timezone
    current_time = models.Issue.get_current_time()
    logger.debug(f"Creating issue at local time: {current_time}")

    db_issue = models.Issue(
        query=issue.query,
        user_id=user_id,
        product_code=product_code,
        product_name=product_name,
        response=response,
        created_at=current_time
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue 