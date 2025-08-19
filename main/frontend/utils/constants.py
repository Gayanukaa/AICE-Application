import os

# Use environment variable for API base URL, fallback to localhost for local development
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
