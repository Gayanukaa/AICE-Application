# Use Python 3.11 slim image as base
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
COPY main/frontend/requirements.txt ./frontend-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r frontend-requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p /app/main/src/data/logs \
    && mkdir -p /app/main/src/data/report \
    && mkdir -p /app/main/src/db

# Set permissions for data directories
RUN chmod -R 755 /app/main/src/data \
    && chmod -R 755 /app/main/src/db

# Expose ports
EXPOSE 8000 8501

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Function to start backend\n\
start_backend() {\n\
    echo "Starting backend server..."\n\
    cd /app/main/src\n\
    uvicorn app:app --host 0.0.0.0 --port 8000 &\n\
    BACKEND_PID=$!\n\
    echo "Backend started with PID: $BACKEND_PID"\n\
}\n\
\n\
# Function to start frontend\n\
start_frontend() {\n\
    echo "Starting frontend server..."\n\
    cd /app/main/frontend\n\
    streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &\n\
    FRONTEND_PID=$!\n\
    echo "Frontend started with PID: $FRONTEND_PID"\n\
}\n\
\n\
# Check command line argument\n\
case "$1" in\n\
    "backend")\n\
        echo "Starting backend only..."\n\
        cd /app/main/src\n\
        exec uvicorn app:app --host 0.0.0.0 --port 8000\n\
        ;;\n\
    "frontend")\n\
        echo "Starting frontend only..."\n\
        cd /app/main/frontend\n\
        exec streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0\n\
        ;;\n\
    "both"|"")\n\
        echo "Starting both backend and frontend..."\n\
        start_backend\n\
        start_frontend\n\
        \n\
        # Wait for any process to exit\n\
        wait -n\n\
        \n\
        # Exit with status of process that exited first\n\
        exit $?\n\
        ;;\n\
    *)\n\
        echo "Usage: $0 {backend|frontend|both}"\n\
        echo "  backend  - Start only the backend API server"\n\
        echo "  frontend - Start only the frontend Streamlit app"\n\
        echo "  both     - Start both services (default)"\n\
        exit 1\n\
        ;;\n\
esac' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["both"]
