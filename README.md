# AI College Exploration (AICE)

AICE is a multi-agent system to help students explore and apply to universities worldwide. It provides:

- **AI-Powered Essay Writing Assistant**
  - Structure & outline uploaded personal statements and supplemental essays
  - Grammar, tone & clarity improvements
  - Real-time feedback aligned with university expectations

- **University Info Retrieval & Program Comparison**
  - Scrape admissions requirements, deadlines, fees & scholarships
  - Normalize into a consistent JSON schema
  - Side-by-side program comparisons on cost, ranking, curriculum & funding

## Getting Started

### Prerequisites

- Python 3.10+
- Streamlit & HTTPX for the frontend

### Backend Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/Gayanukaa/AICE-Backend.git
   cd AICE-Backend
   ````

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   Copy `.env.example` to `.env` and set your OpenAI/Azure credentials:

   ```text
   OPENAI_API_KEY=...
   USE_AZURE_OPENAI=true
   AZURE_OPENAI_DEPLOYMENT_NAME=...
   AZURE_OPENAI_API_KEY=...
   OPENAI_API_VERSION=...
   ```

4. **Start the API**

   ```bash
   cd main/src
   uvicorn app:app --reload --port 8000
   ```

   The backend will be available at `http://localhost:8000/docs`.

### Frontend Setup

1. **Install frontend deps**

   ```bash
   cd main/frontend
   pip install -r requirements.txt
   ```

2. **Run the Streamlit app**

   ```bash
   streamlit run streamlit_app.py
   ```

## 📄 License

This project is licensed under a proprietary license.
