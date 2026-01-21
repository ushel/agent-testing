# --------------------------------------------------
# Imports
# --------------------------------------------------
from inputs.gravity_rules import GRAVITY_RULES
from inputs.internet_guidelines import INTERNET_GUIDELINES
from inputs.domain_expertise import DOMAIN_EXPERTISE

from gan.edge_dataset_planner import plan_edge_dataset
from llm.dataset_author import write_dataset

from datasets.validator import validate_dataset

from memory.dataset_memory_fetcher import fetch_dataset_summaries
from memory.dataset_repository import save_dataset
from memory.evaluation_repository import save_evaluation

from agents.sample_math_agent import run_agent
from evaluation.runner import evaluate
from evaluation.evaluation_writer import save_evaluation_artifact

from deployment.gate import should_deploy

# Graph (Neo4j)
from retrieval.graphite_adapter import GraphiteAdapter


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------
def main():
    print("\n🚀 Starting Agent Evaluation Pipeline\n")

    # --------------------------------------------------
    # Fetch previous dataset memory (avoid duplicates)
    # --------------------------------------------------
    history = fetch_dataset_summaries(
        DOMAIN_EXPERTISE["agent_type"]
    )

    # --------------------------------------------------
    # Plan edge cases (GAN-inspired)
    # --------------------------------------------------
    gan_plan = plan_edge_dataset()

    # --------------------------------------------------
    # Generate dataset (LLM as dataset author)
    # --------------------------------------------------
    dataset = write_dataset(
        gravity=GRAVITY_RULES,
        internet=INTERNET_GUIDELINES,
        domain=DOMAIN_EXPERTISE,
        history=history,
        gan_plan=gan_plan
    )

    # --------------------------------------------------
    # Validate dataset structure
    # --------------------------------------------------
    validate_dataset(dataset)

    # --------------------------------------------------
    # Persist dataset (DB only)
    # --------------------------------------------------
    save_dataset(dataset)

    # --------------------------------------------------
    # Index dataset into Graphite (Neo4j)
    # --------------------------------------------------
    try:
        graph = GraphiteAdapter()

        graph.index_dataset(
            dataset_id=dataset["dataset_name"],
            agent_type=DOMAIN_EXPERTISE["agent_type"],
            domain=DOMAIN_EXPERTISE["domain"],
            intent=dataset["intent"],
            rows=dataset["rows"],
            capabilities=DOMAIN_EXPERTISE.get("capabilities", [])
        )

        print("Dataset indexed into Graphite")

    except Exception as e:
        print(f"Graph indexing skipped: {e}")

    finally:
        try:
            graph.close()
        except Exception:
            pass

    # --------------------------------------------------
    # Evaluate agent on dataset
    # --------------------------------------------------
    score, row_results = evaluate(
        run_agent,
        dataset
    )

    print("\nAgent score:", score)

    # --------------------------------------------------
    # Deployment gate decision
    # --------------------------------------------------
    passed = should_deploy(score)

    # --------------------------------------------------
    # Persist evaluation results (DB)
    # --------------------------------------------------
    run_id = save_evaluation(
        dataset_name=dataset["dataset_name"],
        agent_type=DOMAIN_EXPERTISE["agent_type"],
        score=score,
        passed=passed,
        row_results=row_results
    )

    print(f"Evaluation results saved (run_id={run_id})")

    # --------------------------------------------------
    # Persist evaluation artifact (TEXT FILE)
    # --------------------------------------------------
    artifact_path = save_evaluation_artifact(
        dataset,
        score,
        row_results
    )

    print(f"Evaluation artifact saved → {artifact_path}")

    # --------------------------------------------------
    # Final deployment decision
    # --------------------------------------------------
    if passed:
        print("\nDEPLOY AGENT")
    else:
        failed = [r for r in row_results if not r["passed"]]
        print(f"\nBLOCK DEPLOYMENT — {len(failed)} failed test(s)")


# --------------------------------------------------
# Entry point
# --------------------------------------------------
if __name__ == "__main__":
    main()
