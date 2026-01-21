# --------------------------------------------------
# Graphite Adapter (Neo4j Semantic + Tool-Aware Retrieval)
# --------------------------------------------------

import os
from neo4j import GraphDatabase
from typing import List, Dict


class GraphiteAdapter:
    """
    Graph-based dataset indexing and retrieval using Neo4j.

    Supports:
    - Capability-aware ranking
    - Tool-call visibility
    - Dataset → Row → Tool traceability
    """

    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password)
        )

    # --------------------------------------------------
    # Dataset + Tool Indexing
    # --------------------------------------------------
    def index_dataset(
        self,
        dataset_id: str,
        agent_type: str,
        domain: str,
        intent: str,
        rows: List[Dict],
        capabilities: List[str]
    ) -> None:
        """
        Index a dataset with row-level semantic metadata.
        """

        with self.driver.session() as session:

            # -----------------------------
            # Core nodes
            # -----------------------------
            session.run(
                """
                MERGE (a:Agent {name: $agent_type})
                MERGE (d:Dataset {id: $dataset_id})
                MERGE (dom:Domain {name: $domain})
                MERGE (i:Intent {name: $intent})

                MERGE (a)-[:OPERATES_IN]->(dom)
                MERGE (d)-[:TARGETS_DOMAIN]->(dom)
                MERGE (d)-[:HAS_INTENT]->(i)
                """,
                agent_type=agent_type,
                dataset_id=dataset_id,
                domain=domain,
                intent=intent
            )

            # -----------------------------
            # Capabilities
            # -----------------------------
            for cap in capabilities:
                session.run(
                    """
                    MERGE (c:Capability {name: $cap})
                    MERGE (a:Agent {name: $agent_type})-[:HAS_CAPABILITY]->(c)
                    MERGE (d:Dataset {id: $dataset_id})-[:TESTS_CAPABILITY]->(c)
                    """,
                    cap=cap,
                    agent_type=agent_type,
                    dataset_id=dataset_id
                )

            # -----------------------------
            # Row-level indexing
            # -----------------------------
            for idx, row in enumerate(rows):
                difficulty = row.get("difficulty", "unknown")
                expected_tools = row.get("expected_tools", [])

                session.run(
                    """
                    MERGE (r:TestRow {dataset_id: $dataset_id, row_index: $index})
                    MERGE (d:Dataset {id: $dataset_id})-[:HAS_ROW]->(r)

                    MERGE (diff:Difficulty {level: $difficulty})
                    MERGE (r)-[:HAS_DIFFICULTY]->(diff)
                    """,
                    dataset_id=dataset_id,
                    index=idx,
                    difficulty=difficulty
                )

                for tool in expected_tools:
                    session.run(
                        """
                        MERGE (t:Tool {name: $tool})
                        MERGE (r:TestRow {dataset_id: $dataset_id, row_index: $index})
                              -[:EXPECTS_TOOL]->(t)
                        """,
                        tool=tool,
                        dataset_id=dataset_id,
                        index=idx
                    )

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------
    def wipe_graph(self):
        """
        ⚠️ Deletes ALL nodes and relationships.
        Use only for dev / reset.
        """
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def close(self):
        self.driver.close()
