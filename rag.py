import re
from typing import Dict, Any
from app.services.groq_service import GroqService
from app.graph_db import GraphDB


class RAGEngine:
    def __init__(self):
        self.llm = GroqService()
        self.db = GraphDB()

    # 🔷 Step 1: Generate Cypher
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
- No CREATE, DELETE, MERGE
- Return relevant nodes and relationships

Question:
{query}

Return ONLY Cypher query.
"""

        res = await self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        cypher = res["choices"][0]["message"]["content"]
        return self.clean_cypher(cypher)

    # 🔥 Safety Filter (VERY IMPORTANT)
    def clean_cypher(self, cypher: str) -> str:
        cypher = cypher.strip()

        # Remove markdown blocks
        cypher = re.sub(r"```.*?```", "", cypher, flags=re.DOTALL)

        # Basic safety checks
        forbidden = ["CREATE", "DELETE", "MERGE", "SET"]
        for word in forbidden:
            if word in cypher.upper():
                raise ValueError(f"Unsafe Cypher detected: {word}")

        return cypher

    # 🔷 Step 2: Query Graph
    def query_graph(self, cypher: str):
        try:
            return self.db.run_query(cypher)
        except Exception as e:
            print("❌ Cypher failed:", e)
            return []

    # 🔷 Step 3: Build Answer
    async def generate_answer(self, query: str, graph_data: Any):
        prompt = f"""
Answer the question using the graph data.

Graph Data:
{graph_data}

Question:
{query}

Answer clearly and concisely.
"""

        res = await self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        return res["choices"][0]["message"]["content"]

    # 🔷 Step 4: Format Graph for UI
    def format_graph(self, records):
        nodes = {}
        links = []

        for record in records:
            for key, value in record.items():
                try:
                    if hasattr(value, "items"):  # Node
                        name = value.get("name")
                        if name:
                            nodes[name] = {
                                "id": name,
                                "group": list(value.keys())[0] if hasattr(value, "keys") else "Unknown"
                            }
                except:
                    pass

        return {
            "nodes": list(nodes.values()),
            "links": links
        }

    # 🔷 Full Pipeline
    async def ask(self, query: str) -> Dict[str, Any]:
        try:
            # 1. Generate Cypher
            cypher = await self.generate_cypher(query)

            # 2. Query DB
            graph_records = self.query_graph(cypher)

            # 3. Generate Answer
            answer = await self.generate_answer(query, graph_records)

            # 4. Format Graph
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