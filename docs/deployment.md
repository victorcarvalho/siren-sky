# SirenSky deployment guide

This document provides instructions for deploying the SirenSky platform to cloud providers, specifically highlighting configurations for platforms like Render and Docker container setups.

## Render build error resolution

### The issue
During deployment on Render, the build failed with this compiler error:
```
../meson.build:78:0: ERROR: Unknown compiler(s): [['gfortran'], ['flang-new'], ...]
...
error: metadata-generation-failed (scipy)
```
This occurred because `requirements.txt` was generated via `pip freeze`, which included heavy data-science libraries like `scipy` and `scikit-learn` that were installed in the local virtual environment but never imported or used in the code. Because Render's default Python builder lacks a Fortran compiler (`gfortran`), `pip` failed to compile `scipy` from source.

### The resolution
We uninstalled `scipy`, `scikit-learn`, and other unused legacy packages (like `Flask`, `alembic`, `matplotlib`, `joblib`, and `threadpoolctl`) from the local virtual environment. We then regenerated [backend/requirements.txt](file:///Users/victor/Dev/siren-sky/backend/requirements.txt) using:

```bash
pip freeze > backend/requirements.txt
```

This keeps the virtual environment clean. When deploying now, Render will download pre-compiled binary wheels for the remaining dependencies (such as `pandas` and `mlflow`), bypassing the need for a C/Fortran compiler build stage entirely.

---

## Deploying to Render

To deploy your application on Render, follow these steps:

### Option A: Streamlit web application (recommended)
Deploy the Streamlit web dashboard as a **Web Service**:
1. Create a new **Web Service** on Render and connect it to your GitHub repository.
2. Configure the following build and start settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `streamlit run frontend/streamlit/web_app.py --server.port $PORT --server.address 0.0.0.0`
3. Add the required environment variables in Render's **Environment** tab:
   - `USE_SIMULATED_PREDICTIONS`: `false` (or `true` if testing without API credentials)
   - `OPENAI_API_KEY`: `your-api-key-here`

### Option B: FastAPI REST service
If you want to deploy the FastAPI endpoints for external clients to request classifications:
1. Create a new **Web Service** on Render and connect it to your GitHub repository.
2. Configure the following build and start settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.api:app --host 0.0.0.0 --port $PORT`
3. Add the required environment variables:
   - `USE_SIMULATED_PREDICTIONS`: `false`
   - `OPENAI_API_KEY`: `your-api-key-here`

---

## Containerized deployment (Docker)

To deploy the application to container registries or run it locally using Docker, you can use the following production-ready configuration.

Create a `Dockerfile` in the root of the project:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "frontend/streamlit/web_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
