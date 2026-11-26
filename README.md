# AI Document Assistant

AI Document Assistant is a FastAPI backend for uploading PDF/TXT documents, retrieving relevant content with vector search, and chatting with an LLM. It uses PostgreSQL, Redis, Qdrant, FastEmbed, and Groq.

## Run the backend locally

### Requirements

- Python 3.11 or newer
- Docker Desktop with Docker Compose (used here to run PostgreSQL, Redis, and Qdrant)
- A Groq API key to use the chat endpoint

The repository has a Compose file for the supporting services; the API itself runs as a regular Python application. A Gradio frontend is not needed to run or test the API.

### 1. Get the code and install dependencies

```bash
git clone <repository-url>
cd ai_document_assistant
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install the project's dependencies from `requirements.txt`:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Start the supporting services

From the project directory, start PostgreSQL, Redis, and Qdrant:

```bash
docker compose up -d postgres redis qdrant
```

Wait until PostgreSQL is ready:

```bash
docker compose ps
```

The Compose file publishes these local ports:

| Service | Address |
|---|---|
| PostgreSQL | `localhost:5433` |
| Redis | `localhost:6379` |
| Qdrant HTTP API | `localhost:6333` |
| Qdrant gRPC | `localhost:6334` |

### 3. Configure the application

Create a file named `.env` in the project root with the following settings. Replace the Groq placeholder with your own key:

```dotenv
APP_NAME=AI Document Assistant
DEBUG=True
DATABASE_URL=postgresql+psycopg://admin:12345@localhost:5433/document_assistant
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=documents
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=openai/gpt-oss-120b
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

The database URL and local service credentials above match the development settings in `docker-compose.yml`. Keep `.env` private and never commit real API keys.

### 4. Start the API

```bash
python -m uvicorn app.main:app --reload
```

Uvicorn starts the API at `http://127.0.0.1:8000`. On startup, the application creates its PostgreSQL tables. The first embedding request may take longer because FastEmbed downloads its model.

Open the interactive API documentation in a browser:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- API root: <http://127.0.0.1:8000/>

Use `/docs` to inspect endpoints, submit requests, and see their schemas directly in your browser. The API root (`GET /`) returns a JSON status message. There is no separate `/health` endpoint.

## API endpoints

### Upload a document

`POST /api/v1/documents/ingest` accepts a PDF or UTF-8 TXT file as multipart form data. The optional `chunking_strategy` is `recursive` (default) or `fixed`. Maximum upload size is 10 MB.

You can try the endpoint in Swagger UI by expanding **POST /api/v1/documents/ingest**, selecting **Try it out**, choosing a file, and executing the request.

### Send a chat message

`POST /api/v1/chat/message` accepts JSON:

```json
{
  "message": "Summarize the uploaded document.",
  "session_id": "optional-session-id",
  "top_k": 5
}
```

`message` is required (1–2000 characters); `session_id` is optional and generated when omitted; `top_k` is optional (1–10, defaults to 5). Chat requests need working Redis, Qdrant, and a valid `GROQ_API_KEY`. Upload a document first to ask questions about its content.

## Stop the services

Stop the API with **Ctrl+C**. Stop the supporting containers with:

```bash
docker compose down
```

Compose uses named volumes, so the database, Redis, and Qdrant data are retained. To remove the stored data as well, run `docker compose down -v`.

## Troubleshooting

- **Missing `DATABASE_URL`:** Confirm `.env` exists in the project root and contains the database settings above.
- **Database connection refused:** Check `docker compose ps` and wait for PostgreSQL to finish starting.
- **Redis or Qdrant connection errors:** Confirm their containers are running and their `.env` URLs use `localhost` with the ports shown above.
- **Chat fails:** Check that `GROQ_API_KEY` is valid and that Redis and Qdrant are available.
- **PowerShell blocks virtual environment activation:** Run `python -m pip install -r requirements.txt` using the active Python environment, or use Command Prompt activation with `.\.venv\Scripts\activate.bat`.
