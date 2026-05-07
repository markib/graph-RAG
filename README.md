# Graph RAG API

A Neo4j + Groq powered Graph RAG (Retrieval-Augmented Generation) system.

## Features
- **Graph RAG**: Uses Neo4j to store and retrieve structured knowledge graph data.
- **Groq Integration**: Powers the intelligence layer for RAG queries.
- **FastAPI Backend**: Provides REST endpoints for querying, data ingestion, and graph visualization.
- **Frontend Support**: Includes CORS configuration for React frontend integration.

## Getting Started

### Prerequisites
- Python 3.11+
- Neo4j database instance
- Groq API key

### Installation
1. Clone the repository.
2. Install dependencies (using `uv` or `pip`):
   ```bash
   uv sync
   ```
3. Set up your environment variables:
   Create a `.env` file and add your Neo4j and Groq credentials.

### Running the Application
Start the FastAPI server:
```bash
uvicorn main:app --reload
```

## API Endpoints
- `GET /`: Health check.
- `GET /ask?q=<query>`: Ask a question to the RAG system.
- `GET /graph`: Retrieve the graph data for visualization.
- `POST /ingest`: Ingest data into the graph.
- `DELETE /graph/clear`: Clear the graph database (Dev only).

## Architecture
- `main.py`: FastAPI application entry point.
- `app/rag.py`: Core RAG engine logic.
- `app/graph_db.py`: Neo4j database interactions.
- `ingest.py` / `extract.py`: Scripts for processing and preparing data.
