import os
from typing import Dict, Any
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


class GraphDB:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )

    def close(self):
        self.driver.close()

    # ------------------------
    # Helpers
    # ------------------------

    def normalize_label(self, label: str) -> str:
        return label.strip().capitalize()

    def normalize_name(self, name: str) -> str:
        return name.strip()

    # ------------------------
    # Core Query
    # ------------------------

    def run_query(self, query: str, params: dict = None):
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    # ------------------------
    # Entity
    # ------------------------

    def merge_entity(self, label: str, name: str, properties: Dict = None):
        label = self.normalize_label(label)
        name = self.normalize_name(name)

        query = f"""
        MERGE (n:{label} {{name: $name}})
        SET n += $props
        RETURN n
        """

        with self.driver.session() as session:
            session.run(query, {
                "name": name,
                "props": properties or {}
            })

    # ------------------------
    # Relationship
    # ------------------------

    def merge_relationship(
        self,
        source_name: str,
        target_name: str,
        rel_type: str,
        properties: Dict = None
    ):
        source_name = self.normalize_name(source_name)
        target_name = self.normalize_name(target_name)
        rel_type = rel_type.strip().upper()

        query = f"""
        MATCH (a {{name: $source}})
        MATCH (b {{name: $target}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $props
        RETURN r
        """

        with self.driver.session() as session:
            session.run(query, {
                "source": source_name,
                "target": target_name,
                "props": properties or {}
            })

    # ------------------------
    # INGEST (FIXED)
    # ------------------------

    def ingest(self, data: Dict[str, Any]):
        # 1. Create all nodes FIRST
        for entity in data.get("entities", []):
            label = entity.get("type")
            name = entity.get("name")

            if not label or not name:
                continue

            self.merge_entity(
                label=label,
                name=name,
                properties=entity.get("properties", {})
            )

        # 2. Then create relationships (NO entity_map needed)
        for rel in data.get("relationships", []):
            source = rel.get("source")
            target = rel.get("target")
            rel_type = rel.get("type")

            if not source or not target or not rel_type:
                continue

            self.merge_relationship(
                source_name=source,
                target_name=target,
                rel_type=rel_type,
                properties=rel.get("properties", {})
            )

    # ------------------------
    # CLEAR DB
    # ------------------------

    def clear(self):
        self.run_query("MATCH (n) DETACH DELETE n")

    # ------------------------
    # GRAPH FETCH
    # ------------------------

    def get_graph(self):
        query = """
        MATCH (a)-[r]->(b)
        RETURN a, r, b
        LIMIT 200
        """

        with self.driver.session() as session:
            result = session.run(query)
            records = list(result)

        nodes = {}
        links = []

        for record in records:
            a = record["a"]
            b = record["b"]
            r = record["r"]

            nodes[a["name"]] = {
                "id": a["name"],
                "group": list(a.labels)[0] if hasattr(a, "labels") else "Unknown"
            }

            nodes[b["name"]] = {
                "id": b["name"],
                "group": list(b.labels)[0] if hasattr(b, "labels") else "Unknown"
            }

            links.append({
                "source": a["name"],
                "target": b["name"],
                "label": r.type if hasattr(r, "type") else "UNKNOWN"
            })

        return {
            "nodes": list(nodes.values()),
            "links": links
        }