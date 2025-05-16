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
   git clone https://github.com/your-org/aice.git
   cd aice
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
   uvicorn src.api.app:app --reload
   ```

   The backend will be available at `http://localhost:8000/`.

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

   Navigate to `http://localhost:8501` and use the sidebar to switch between:

   - *Essay Writing*
   - *Program Analysis*

## 📄 License

This project is licensed under a proprietary license.
