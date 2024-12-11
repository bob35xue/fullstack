from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from .. import crud
from ..database import get_session
from ..models import IssueCreate, IssueInDB
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/issues",
    tags=["issues"]
)

# Get classifier from main app state
def get_classifier():
    from ..main import classifier
    return classifier

class QueryRequest(BaseModel):
    query: str

@router.post("/classify/")
async def classify_query(
    request: QueryRequest,
    req: Request,
    response: Response,
    db: Session = Depends(get_session)
):
    logger.info(f"Received classification request: {request.query}")
    logger.debug(f"Session data: {dict(req.session)}")
    
    user_id = req.session.get("user_id")
    if not user_id:
        logger.warning("Unauthorized access attempt - no user_id in session")
        raise HTTPException(
            status_code=401,
            detail="Please log in to use the chatbot"
        )
    
    logger.debug(f"Processing request for user_id: {user_id}")
    
    try:
        from ..main import classifier
        if not classifier:
            logger.error("Classifier not initialized")
            raise HTTPException(status_code=500, detail="Classifier not initialized")
        
        # Classify the query
        product_code, product_name = classifier.classify(request.query)
        logger.info(f"Classification result: {product_name} (code: {product_code})")
        
        # Create issue object
        issue = IssueCreate(query=request.query)
        
        # Save to database
        db_issue = crud.create_user_issue(
            db=db,
            issue=issue,
            user_id=user_id,
            product_code=product_code,
            product_name=product_name,
            response=f"This appears to be a {product_name} related issue"
        )
        logger.debug(f"Created issue record: {db_issue.id}")

        return {
            "query": request.query,
            "product_code": product_code,
            "product_name": product_name,
            "response": f"This appears to be a {product_name} related issue",
            "issue_id": db_issue.id
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/", response_model=IssueInDB)
async def create_issue(
    issue: IssueCreate,
    user_id: int,
    db: Session = Depends(get_session)
):
    try:
        # classifier = get_classifier()
        # product_code, product_name = classifier.classify(issue.query)
        product_code = 999
        product_name = "Unknown"
        
        # Format the response string
        response = f"This appears to be a {product_name} related issue (code: {product_code})"
        
        # Create the issue in the database
        db_issue = crud.create_user_issue(
            db=db,
            issue=issue,
            user_id=user_id,
            product_code=product_code,
            product_name=product_name,
            response=response
        )
        return db_issue
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/user/{user_id}", response_model=List[IssueInDB])
def read_user_issues(user_id: int, db: Session = Depends(get_session)):
    issues = crud.get_user_issues(db, user_id=user_id)
    return issues
