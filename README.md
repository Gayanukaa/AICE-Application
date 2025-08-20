# AI College Exploration (AICE)

AICE (AI College Exploration) is a multi-agent system designed to assist students in exploring and applying to universities globally. It offers a range of AI-powered tools to streamline the college application process.

<div align="center">
  
### AICE Application Demo

[Short walkthrough of the AICE UI and agent flows](main/media/AICE demo.mp4)

</div>

## Features

- **AI Essay Writing Assistant:** Provides support for crafting compelling personal statements and supplemental essays.
- **University Information Retrieval & Program Comparison:** Gathers and compares crucial university program data.
- **Cost Breakdown Analysis:** Analyzes the expenses associated with different programs, providing a clear view of potential costs.
- **Timeline Planner:** Creates personalized timelines for the application process, ensuring students stay on track with important deadlines.
- **Application Checklist Generator:** Generates customized checklists of required documents and tasks for each university a student is applying to.
- **Interview Preparation:** Offers interview questions and response guidelines to help students prepare for university interviews.

## Getting Started

### Docker Setup (Recommended)

**[Complete Docker Setup Guide](DOCKER_README.md)**
>
> Quick start with Docker:
>
> ```bash
> # Clone and setup
> git clone https://github.com/Gayanukaa/AICE-Backend.git
> cd AICE-Backend
> cp .env.example .env
> # Edit .env with your API keys
>
> # Run with Docker
> docker-compose up
> ```

### Manual Setup

#### Backend Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/Gayanukaa/AICE-Backend.git
cd AICE-Backend
```

#### 2. Install Backend Dependencies

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
   SERPER_API_KEY=...
   ```

4. **Start the API**

   ```bash
   cd main/src
   uvicorn app:app --reload --port 8000
   ```

   The backend will be available at `http://localhost:8000/docs`.

#### Frontend Setup

1. **Install Frontend Dependencies**

   ```bash
   cd main/frontend
   pip install -r requirements.txt
   ```

2. **Run the Streamlit App**

   ```bash
   streamlit run streamlit_app.py
   ```

   The frontend will be available at `http://localhost:8501`.

## License

This project is licensed under a proprietary license.
