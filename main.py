from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.rag import RAGEngine
from app.graph_db import GraphDB

load_dotenv()

# Initialize app
app = FastAPI(
    title="Graph RAG API",
    description="Neo4j + Groq powered Graph RAG system",
    version="1.0.0"
)

# 🔷 CORS (React frontend support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production: set frontend URL
    allow_origin_regex=".*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 🔷 Global error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) if str(exc) else "Internal Server Error"},
        headers={"Access-Control-Allow-Origin": "*"},
    )

# 🔷 Core Services
rag = None
db = None
rag_error = None
db_error = None

try:
    rag = RAGEngine()
except Exception as e:
    rag_error = str(e)
    print(f"⚠️  RAG Engine init failed: {rag_error}")

try:
    db = GraphDB()
except Exception as e:
    db_error = str(e)
    print(f"⚠️  Graph DB init failed: {db_error}")


# =========================
# 🔷 HEALTH CHECK
# =========================
@app.get("/")
def health():
    return {
        "status": "ok",
        "message": "Graph RAG API is running"
    }


# =========================
# 🔷 RAG QUERY ENDPOINT
# =========================
@app.get("/ask")
async def ask(q: str):
    """
    Main Graph RAG query endpoint
    """
    if rag is None:
        return {
            "error": rag_error,
            "answer": "RAG system not available",
            "cypher": "",
            "graph": {"nodes": [], "links": []}
        }
    return await rag.ask(q)


# =========================
# 🔷 GRAPH DATA (for React UI)
# =========================
@app.get("/graph")
def get_graph():
    """
    Returns full graph for visualization
    """
    if db is None:
        return {
            "error": db_error,
            "nodes": [],
            "links": []
        }
    return db.get_graph()


# =========================
# 🔷 CLEAR DATABASE (DEV ONLY)
# =========================
@app.delete("/graph/clear")
def clear_graph():
    """
    Danger: deletes all nodes/relationships
    """
    if db is None:
        return {"error": db_error, "message": "Graph DB not available"}
    db.clear()
    return {"message": "Graph cleared successfully"}


# =========================
# 🔷 INGEST DATA (from extract.py output)
# =========================
@app.post("/ingest")
def ingest(data: dict):
    """
    Ingest extracted entities + relationships into Neo4j
    """
    if db is None:
        return {"error": db_error, "message": "Graph DB not available"}
    db.ingest(data)
    return {
        "message": "Data ingested successfully",
        "entities": len(data.get("entities", [])),
        "relationships": len(data.get("relationships", []))
    }