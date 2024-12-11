from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from ..database import get_session, SessionLocal
from ..models import User
from .. import crud
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

# Create a Pydantic model for login request
class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(
    login_data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_session)
):
    # Add CORS headers directly to the response
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    
    user = crud.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        logger.warning(f"Failed login attempt for email: {login_data.email}")
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Set user data in session
    request.session["user_id"] = user.id
    request.session["email"] = user.email
    
    logger.info(f"Successful login for user: {user.email} (ID: {user.id})")
    logger.debug(f"Session data: {request.session}")
    
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser
    }

@router.options("/login")
async def login_options(response: Response):
    # Handle OPTIONS preflight request
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return {}

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_session)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user.email,
        password=user.password,
        full_name=user.full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/")
def get_users(db: Session = Depends(get_session)):
    users = db.query(User).all()
    return users

