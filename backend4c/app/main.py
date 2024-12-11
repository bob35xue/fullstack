import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .classification import issue_classification
from .routers import user_router, issue_router
from .database import Base, engine, init_db, backup_db
from .utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI()

# Configure CORS first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Then add SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here",
    session_cookie="session",
    max_age=3600,  # 1 hour
    same_site="lax",
    https_only=False,
)

# Global classifier variable
classifier = None

@app.on_event("startup")
async def startup_event():
    global classifier
    try:
        # Create backup of existing database if it exists
        backup_db()
        
        # Initialize database if needed
        db_initialized = init_db()
        if db_initialized:
            logger.info("New database initialized")
        else:
            logger.info("Using existing database")
        
        # Initialize classifier
        classifier = issue_classification.IssueClassifier()
        
        # Check if model needs training
        model_path = './data4c/results/model_distill_bert.pth'
        if not os.path.exists(model_path):
            logger.info("Training new model...")
            success = classifier.train()
            if not success:
                logger.error("Failed to train model")
                raise Exception("Model training failed")
        
        logger.info("Startup completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    try:
        # Create final backup when shutting down
        backup_db()
        logger.info("Shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Backend is running"}

# Include routers
app.include_router(user_router.router)
app.include_router(issue_router.router)

# Create database tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

#.venv\Scripts\activate
# .venv\Scripts\pip freeze --local  > installed_packages.txt
# uvicorn backend4c.app.main:app --reload
# cd frontend4c
# npm install
# npm start
# Ctrl+L  for cursor
# cd frontend4c
#set NODE_OPTIONS=--openssl-legacy-provider
# npm start 

# docker
# Build and start the containers
# docker-compose up --build

# Stop the containers
# docker-compose down

# View logs
#docker-compose logs -f

# Rebuild a specific service
# docker-compose up --build backend