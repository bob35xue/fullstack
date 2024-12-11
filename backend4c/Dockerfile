FROM python:3.11-slim-buster as builder

WORKDIR /app

# Copy requirements first
COPY backend4c/requirements.txt .
RUN pip install -r requirements.txt

# Create the directory structure that matches your local setup
RUN mkdir -p /app/data4c/results

# Copy the model, database, and training data with the same structure as local
COPY data4c/results/model_distill_bert.pth /app/data4c/results/
COPY data4c/db4chatbot.db /app/data4c/
COPY data4c/customer_queries.csv /app/data4c/

# Copy the application code maintaining the structure
COPY backend4c/app /app/app
COPY backend4c/requirements*.txt /app/

# Set environment variables to match the directory structure
ENV PYTHONPATH=/app
ENV DB_DIRECTORY=/app/data4c
ENV MODEL_DIRECTORY=/app/data4c/results
ENV TRAINING_DATA_DIRECTORY=/app/data4c

# Your CMD or ENTRYPOINT command here 