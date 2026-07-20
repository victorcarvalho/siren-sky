FROM python:3.13-slim

WORKDIR /app

# Install basic system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy codebase
COPY backend/ ./backend/
COPY frontend/ ./frontend/


# Expose Streamlit (8501) and FastAPI (8000) ports
EXPOSE 8501
EXPOSE 8000

# Default to running the Streamlit dashboard
ENTRYPOINT ["streamlit", "run", "frontend/streamlit/web_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
