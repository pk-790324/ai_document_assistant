# AI Document Assistant

AI Document Assistant is a document-aware chat application built with FastAPI, LangChain, Qdrant, PostgreSQL, Redis, Groq, FastEmbed, and Gradio.

It provides:

- PDF and TXT document ingestion
- Recursive or fixed-size text chunking
- Semantic document search using vector embeddings
- Retrieval-Augmented Generation (RAG) chat
- Conversation history stored in Redis
- Interview booking through a structured multi-turn conversation
- Confirmed bookings persisted in PostgreSQL
- A Gradio web interface and REST API

## How It Works

1. A user uploads a PDF or TXT file through the Gradio interface or API.
2. The backend validates and extracts the document text.
3. The text is split into chunks using the selected chunking strategy.
4. FastEmbed creates vector embeddings for each chunk.
5. Chunk vectors and metadata are stored in Qdrant.
6. Chat messages are classified as document-related questions or interview booking requests.
7. RAG questions retrieve relevant chunks and generate an answer with Groq.
8. Booking details are collected in Redis before the confirmed booking is stored in PostgreSQL.

## Technology Stack

- **Backend:** FastAPI, Uvicorn
- **Frontend:** Gradio
- **LLM:** Groq through LangChain
- **Embeddings:** FastEmbed with `BAAI/bge-small-en-v1.5`
- **Vector database:** Qdrant
- **Session and booking drafts:** Redis
- **Relational database:** PostgreSQL and SQLAlchemy
- **Document processing:** PyMuPDF for PDF files
- **Validation:** Pydantic and Pydantic Settings
- **Testing:** pytest and httpx

## Project Structure

```text
ai_document_assistant/
├── app/
│   ├── api/v1/           # FastAPI chat and document routes
│   ├── core/             # Application settings and logging
│   ├── database/         # SQLAlchemy engine and database session
│   ├── models/           # PostgreSQL document and booking models
│   ├── repositories/     # Database repository operations
│   ├── schemas/          # Request and response models
│   ├── services/         # RAG, chat, booking, chunking, and vector services
│   └── utils/            # Upload validation
├── tests/                # pytest test modules
├── main.py               # Gradio frontend
├── docker-compose.yml    # PostgreSQL, Redis, and Qdrant services
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

## Prerequisites

Install or start the following services:

- Python 3.11 or newer
- Docker and Docker Compose
- A Groq API key

The default local service URLs are:

| Service | Default URL |
|---|---|
| PostgreSQL | `postgresql+psycopg://admin:12345@localhost:5433/document_assistant` |
| Redis | `redis://localhost:6379/0` |
| Qdrant | `http://localhost:6333` |

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd ai_document_assistant
```

Install dependencies and create the uv environment:

```bash
uv sync
```

## Configuration

Create a `.env` file in the project root:

```dotenv
# Application
APP_NAME=AI Document Assistant
DEBUG=True

# PostgreSQL
DATABASE_URL=postgresql+psycopg://admin:12345@localhost:5433/document_assistant

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=documents

# Groq
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=openai/gpt-oss-120b

# Embeddings
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

Keep API keys out of source control. If a Groq key has already been committed or shared, revoke it and create a replacement key.

## Running the Application

Docker Compose starts PostgreSQL, Redis, and Qdrant together:

```bash
docker compose up -d
```

Check that all containers are running:

```bash
docker compose ps
```

The Compose file provides:

| Container | Host port |
|---|---|
| `ai_postgres` | `5433` |
| `ai_redis` | `6379` |
| `ai_qdrant` | `6333` and `6334` |

The application creates the `documents` and `bookings` tables automatically when the FastAPI lifespan starts.

To stop the infrastructure containers:

```bash
docker compose down
```

This preserves database and vector data because Compose uses named volumes. To remove the volumes and their stored data as well:

```bash
docker compose down -v
```

### 1. Start the FastAPI backend

```bash
uv run uvicorn app.main:app --reload
```

The backend is available at:

- API root: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health endpoint: `http://127.0.0.1:8000/health`

### 2. Start the Gradio frontend

Open another terminal, activate the virtual environment, and run:

```bash
uv run python main.py
```

Gradio launches a local web interface, usually at `http://127.0.0.1:7860`.

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "message": "AI Document Assistant API is running"
}
```

### Upload and Ingest a Document

```http
POST /api/v1/documents/ingest
Content-Type: multipart/form-data
```

Form fields:

- `file`: PDF or UTF-8 TXT file
- `chunking_strategy`: `recursive` or `fixed`

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/ingest" \
  -F "file=@./document.pdf" \
  -F "chunking_strategy=recursive"
```

Upload limits:

- Maximum file size: 10 MB
- Supported extensions: `.pdf` and `.txt`

### Send a Chat Message

```http
POST /api/v1/chat/message
Content-Type: application/json
```

Request body:

```json
{
  "message": "Summarize the uploaded document.",
  "session_id": "optional-session-id",
  "top_k": 5
}
```

- `message`: Required, 1–2000 characters
- `session_id`: Optional; omitted values receive a generated UUID
- `top_k`: Optional, 1–10; defaults to 5

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"What is the main topic?\",\"top_k\":5}"
```

Example response:

```json
{
  "session_id": "generated-or-supplied-session-id",
  "intent": "rag",
  "message": "The answer generated by the RAG service.",
  "sources": [],
  "booking_id": null,
  "booking_status": null
}
```

## Interview Booking Flow

Start a booking by asking to schedule an interview. The booking service collects:

- Candidate name
- Email address
- Interview date in `YYYY-MM-DD` format
- Interview time in `HH:MM` 24-hour format

The draft is retained in Redis for 24 hours. The assistant asks for missing details, validates that the appointment is in the future, and waits for explicit confirmation before saving a confirmed booking in PostgreSQL.

Booking dates and times use the `Asia/Kathmandu` timezone.

## Testing

Run the test suite:

```bash
pytest
```

Run a single test module:

```bash
pytest tests/test_chat.py
```