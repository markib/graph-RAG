import re
from typing import Dict, Any
from app.services.groq_service import GroqService
from app.graph_db import GraphDB


class RAGEngine:
    def __init__(self):
        self.llm = GroqService()
        self.db = GraphDB()

    async def generate_cypher(self, query: str) -> str:
        prompt = f"""
You are a Neo4j expert.

Schema:
(User)-[:BOUGHT]->(Product)
(Product)-[:BELONGS_TO]->(Category)
(Product)-[:SOLD_BY]->(Store)

Convert the question into Cypher query.

Rules:
- Use only MATCH and RETURN
- No CREATE, DELETE, MERGE, SET
- Return relevant nodes and relationships
- Do not modify the database

Question:
{query}

Return ONLY Cypher query.
"""

        res = await self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        cypher = res["choices"][0]["message"]["content"]
        return self.clean_cypher(cypher)

    def clean_cypher(self, cypher: str) -> str:
        cypher = cypher.strip()
        cypher = re.sub(r"```.*?```", "", cypher, flags=re.DOTALL)
        cypher = re.sub(r"\s+", " ", cypher).strip()

        # Remove SET clauses while keeping MATCH/RETURN statements intact.
        cypher = re.sub(r"\bSET\b.*?(?=\bRETURN\b|$)", "", cypher, flags=re.IGNORECASE)

        forbidden = ["CREATE", "DELETE", "MERGE"]
        for word in forbidden:
            if re.search(rf"\b{word}\b", cypher, flags=re.IGNORECASE):
                raise ValueError(f"Unsafe Cypher detected: {word}")

        if not re.search(r"\bMATCH\b", cypher, flags=re.IGNORECASE) or not re.search(r"\bRETURN\b", cypher, flags=re.IGNORECASE):
            raise ValueError("Unsafe Cypher detected: Query must use MATCH and RETURN only")

        return cypher.strip()

    def query_graph(self, cypher: str):
        try:
            return self.db.run_query(cypher)
        except Exception as e:
            print("❌ Cypher failed:", e)
            return []

    def graph_to_context(self, records: Any) -> str:
        if not records:
            return "No graph data available."
        
        lines = []
        for record in records:
            if isinstance(record, dict):
                lines.append(str(record))
            else:
                lines.append(str(record))
        
        return "\n".join(lines)

    async def generate_answer(self, query: str, graph_data: Any) -> str:
        context = self.graph_to_context(graph_data)

        prompt = f"""
You are a Graph RAG assistant.

Use ONLY the graph context below.

GRAPH CONTEXT:
{context}

QUESTION:
{query}

Rules:
- If context is empty, say "No relevant data found in graph"
- Do NOT hallucinate
- Answer strictly based on graph

Answer:
"""

        res = await self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        return res["choices"][0]["message"]["content"]

    def format_graph(self, records):
        nodes = {}
        links = []

        for record in records:
            for key, value in record.items():
                try:
                    if hasattr(value, "items"):
                        name = value.get("name")
                        if name:
                            nodes[name] = {
                                "id": name,
                                "group": list(value.keys())[0] if hasattr(value, "keys") else "Unknown"
                            }
                except Exception:
                    pass

        return {
            "nodes": list(nodes.values()),
            "links": links
        }

    async def ask(self, query: str) -> Dict[str, Any]:
        try:
            cypher = await self.generate_cypher(query)
            graph_records = self.query_graph(cypher)
            answer = await self.generate_answer(query, graph_records)
            graph = self.db.get_graph()

            return {
                "answer": answer,
                "cypher": cypher,
                "graph": graph
            }

        except Exception as e:
            return {
                "error": str(e),
                "answer": "Something went wrong.",
                "cypher": "",
                "graph": {"nodes": [], "links": []}
            }
