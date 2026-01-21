from retrieval.graphite_adapter import GraphiteAdapter

def clean_graph():
    g = GraphiteAdapter()
    with g.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n;")
    g.close()
    print("Graph cleaned successfully")

if __name__ == "__main__":
    clean_graph()
