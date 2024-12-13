# FullStack4Chatbot

A full-stack chatbot application built with FastAPI, SQLite, and React, featuring product classification using DistilBERT. This AI-powered chatbot helps users identify and classify product-related queries.

## Table of Contents
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Tech Stack

### Frontend
- React 19.0.0 for UI components
- React Router DOM 7.0.2 for routing
- Axios 1.7.9 for HTTP requests
- Node.js 16 (Alpine) for runtime environment
- ESLint 8.56.0 for code linting
- Babel plugins for modern JavaScript features

### Backend
- Python 3.11 runtime
- FastAPI 0.115.6 web framework
- SQLAlchemy 2.0.36 ORM
- DistilBERT for NLP classification
- SQLite database
- Uvicorn ASGI server
- PyTorch 2.4.1 for machine learning
- Transformers 4.47.0 for NLP models

### DevOps
- Docker and Docker Compose for containerization
- Health monitoring system
- Volume management for persistent data
- Network configuration for container communication

## Features

### User Management
- User registration and authentication
- Session management with JWT tokens
- Role-based access control (Admin/Regular users)
- Password hashing with bcrypt

### Chatbot Functionality
- Real-time product classification
- Natural language processing
- Multi-product support
- Query history tracking
- Response caching

### AI/ML Capabilities
- DistilBERT-based text classification
- Pre-trained model loading
- Model fine-tuning capabilities
- Confidence score calculation

### System Features
- RESTful API architecture
- Database migrations
- Logging system
- Error handling
- CORS support
- Health monitoring

## Architecture

### System Architecture
```
[Client Browser] ←→ [Frontend Container (React)]
                    ↓
            [Docker Network]
                    ↓
[Backend Container (FastAPI)] ←→ [SQLite Database]
                    ↓
        [DistilBERT Model Service]
```

### Data Flow
1. User submits query through React frontend
2. Request processed by FastAPI backend
3. Query classified by DistilBERT model
4. Result stored in SQLite database
5. Response returned to frontend
6. Chat history updated

## Project Structure

```
fullstack4chatbot/
├── backend4c/
│   ├── app/
│   │   ├── classification/
│   │   │   ├── issue_classification.py
│   │   │   └── models/
│   │   ├── routers/
│   │   │   ├── user_router.py
│   │   │   └── issue_router.py
│   │   ├── utils/
│   │   │   ├── logger.py
│   │   │   └── security.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── main.py
│   ├── data4c/
│   │   ├── logs/
│   │   ├── results/
│   │   └── db4chatbot.db
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend4c/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   ├── tests/
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Installation

### Local Development Setup

1. Clone and setup environment:
```bash
git clone https://github.com/yourusername/fullstack4chatbot.git
cd fullstack4chatbot
```

2. Backend setup:
```bash
cd backend4c
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Frontend setup:
```bash
cd frontend4c
npm install
```

### Docker Setup

1. Build images:
```bash
docker-compose build
```

2. Run containers:
```bash
docker-compose up
```

3. Stop containers:
```bash
docker-compose down
```

## Configuration

### Environment Variables

Backend (.env):
```env
PYTHONUNBUFFERED=1
DATABASE_URL=sqlite:///./data4c/db4chatbot.db
MODEL_PATH=./data4c/results/model_distill_bert.pth
LOG_LEVEL=INFO
```

Frontend (.env):
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_VERSION=1.0.0
```

### Docker Configuration

```yaml
version: '3.8'
services:
  backend:
    build: ./backend4c
    ports: ["8000:8000"]
    volumes: ["./data4c:/app/data4c"]
    
  frontend:
    build: ./frontend4c
    ports: ["3000:3000"]
    depends_on: ["backend"]
```

## API Documentation

### Authentication Endpoints
- `POST /users/login`
  - Request: `{ "email": string, "password": string }`
  - Response: `{ "token": string, "user": User }`

### Classification Endpoints
- `POST /issues/classify`
  - Request: `{ "query": string }`
  - Response: `{ "product_code": int, "product_name": string }`

### History Endpoints
- `GET /issues/history`
  - Response: `{ "issues": Issue[] }`

## Development

### Running Tests
```bash
# Backend tests
cd backend4c
python -m pytest -v

# Frontend tests
cd frontend4c
npm test
```

### Code Style
```bash
# Backend
flake8 backend4c
black backend4c

# Frontend
cd frontend4c
npm run lint
```
