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

        if not self.uri or not self.user or not self.password:
            raise RuntimeError(
                "Neo4j environment variables are missing. "
                "Please set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD."
            )

        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
        except Exception as exc:
            raise RuntimeError(f"Unable to connect to Neo4j: {exc}") from exc

    def close(self):
        self.driver.close()

    # 🔷 Run raw query
    def run_query(self, query: str, params: dict = None):
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    # 🔷 Create or merge entity
    def merge_entity(self, label: str, name: str, properties: Dict = None):
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

    # 🔷 Create relationship
    def merge_relationship(
        self,
        source_name: str,
        source_label: str,
        target_name: str,
        target_label: str,
        rel_type: str,
        properties: Dict = None
    ):
        query = f"""
        MATCH (a:{source_label} {{name: $source}})
        MATCH (b:{target_label} {{name: $target}})
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

    # 🔥 Bulk insert (IMPORTANT)
    def ingest(self, data: Dict[str, Any]):
        """
        Expected format:
        {
          "entities": [...],
          "relationships": [...]
        }
        """

        # Step 1: Insert Entities
        entity_map = {}

        for entity in data.get("entities", []):
            label = entity.get("type")
            name = entity.get("name")

            if not label or not name:
                continue

            self.merge_entity(label, name, entity.get("properties", {}))

            # Save mapping for relationships
            entity_map[name] = label

        # Step 2: Insert Relationships
        for rel in data.get("relationships", []):
            source = rel.get("source")
            target = rel.get("target")
            rel_type = rel.get("type")

            if not source or not target or not rel_type:
                continue

            source_label = entity_map.get(source)
            target_label = entity_map.get(target)

            # Skip if labels unknown
            if not source_label or not target_label:
                continue

            self.merge_relationship(
                source_name=source,
                source_label=source_label,
                target_name=target,
                target_label=target_label,
                rel_type=rel_type,
                properties=rel.get("properties", {})
            )

    # 🔷 Clear DB (for testing)
    def clear(self):
        self.run_query("MATCH (n) DETACH DELETE n")

    # 🔷 Get graph (for React)
    def get_graph(self):
        query = """
        MATCH (a)-[r]->(b)
        RETURN a, r, b
        LIMIT 100
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