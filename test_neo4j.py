from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "password")
)

with driver.session() as session:
    result = session.run("RETURN 1 AS ok")
    print(result.single()["ok"])

