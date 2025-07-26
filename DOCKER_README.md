# Docker Setup for AICE Backend

This document explains how to run the AICE Backend application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (usually comes with Docker Desktop)
- `.env` file with your API keys (copy from `.env.example`)

## Quick Start

### Option 1: Using Docker Compose (Recommended for Development)

1. **Clone and setup environment:**

   ```bash
   git clone https://github.com/Gayanukaa/AICE-Backend.git
   cd AICE-Backend
   cp .env.example .env
   # Edit .env file with your API keys
   ```

2. **Run both backend and frontend:**

   ```bash
   docker-compose up
   ```

   This will start:

   - Backend API at: http://localhost:8000
   - Frontend Streamlit app at: http://localhost:8501

3. **Run services separately:**

   ```bash
   # Start only backend
   docker-compose up aice-backend

   # Start only frontend (in another terminal)
   docker-compose up aice-frontend
   ```

4. **Run combined service:**
   ```bash
   docker-compose --profile combined up aice-combined
   ```

### Option 2: Using Docker directly

1. **Build the image:**

   ```bash
   docker build -t aice-backend .
   ```

2. **Run backend only:**

   ```bash
   docker run -p 8000:8000 --env-file .env aice-backend backend
   ```

3. **Run frontend only:**

   ```bash
   docker run -p 8501:8501 aice-backend frontend
   ```

4. **Run both services:**
   ```bash
   docker run -p 8000:8000 -p 8501:8501 --env-file .env aice-backend both
   ```

## Environment Variables

Make sure your `.env` file contains:

```
OPENAI_API_KEY=your_openai_api_key
USE_AZURE_OPENAI=true
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_KEY=your_azure_api_key
OPENAI_API_VERSION=your_api_version
SERPER_API_KEY=your_serper_api_key
```

## Data Persistence

The Docker setup includes volume mounts for:

- `./main/src/data` - Application data and logs
- `./main/src/db` - SQLite database files

## Development

For development with hot-reload:

```bash
# Start with volume mounts for live code changes
docker-compose up
```

The compose file includes volume mounts that allow you to edit code and see changes without rebuilding.

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Troubleshooting

1. **Port conflicts:** Make sure ports 8000 and 8501 are not in use by other applications
2. **Environment variables:** Ensure your `.env` file is properly configured
3. **Permissions:** If you encounter permission issues, check that the data directories are writable
4. **Logs:** View logs with `docker-compose logs` or `docker logs <container_name>`

## Production Deployment

For production, consider:

- Using environment-specific docker-compose files
- Setting up proper secrets management
- Configuring reverse proxy (nginx)
- Setting up monitoring and logging
- Using health checks
