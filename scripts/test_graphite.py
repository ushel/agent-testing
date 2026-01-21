from retrieval.graphite_adapter import GraphiteAdapter

g = GraphiteAdapter()

g.wipe_graph()  # optional during dev

g.index_dataset(
    dataset_id="math-core-v1",
    agent_type="mathematical",
    domain="math",
    intent="problem_solving",
    difficulties=["easy", "medium", "hard"],
    capabilities=["arithmetic", "algebra", "geometry"]
)

print(g.retrieve_for_agent("mathematical", "math"))
