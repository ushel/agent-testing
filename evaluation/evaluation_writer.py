from pathlib import Path
from datetime import datetime


ARTIFACT_DIR = Path("artifacts")


def _ensure_dir():
    ARTIFACT_DIR.mkdir(exist_ok=True)


def save_evaluation_artifact(
    dataset: dict,
    score: float,
    row_results: list
):
    """
    Save human-readable evaluation results.

    Artifacts contain ONLY evaluation results:
    - prompt
    - expected vs actual
    - tool behavior
    - pass/fail reasoning
    """

    _ensure_dir()

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name = dataset["dataset_name"].replace(" ", "_")

    path = ARTIFACT_DIR / f"{name}_evaluation_{ts}.txt"

    with open(path, "w") as f:
        # --------------------------------------------------
        # Header
        # --------------------------------------------------
        f.write(f"DATASET NAME : {dataset['dataset_name']}\n")
        f.write(f"AGENT TYPE   : {dataset['agent_type']}\n")
        f.write(f"SCORE        : {score}\n\n")

        f.write("=" * 70 + "\n")
        f.write("TEST RESULTS (TOOL-AWARE)\n")
        f.write("=" * 70 + "\n\n")

        # --------------------------------------------------
        # Row-level results
        # --------------------------------------------------
        for row in row_results:
            f.write(f"[{row['row_index']}]\n")
            f.write(f"PROMPT              : {row['prompt']}\n")
            f.write(f"EXPECTED OUTPUT     : {row['expected_output']}\n")
            f.write(f"ACTUAL OUTPUT       : {row['actual_output']}\n")

            # Tool section
            f.write(f"EXPECTED TOOLS      : {row.get('expected_tools', [])}\n")
            f.write(f"ACTUAL TOOLS        : {row.get('actual_tools', [])}\n")
            f.write(f"TOOL EXPECTED       : {row.get('tool_expected', False)}\n")
            f.write(f"TOOL CALLED         : {row.get('tool_called', False)}\n")
            f.write(
                f"CORRECT TOOL CALLED : {row.get('correct_tool_called', False)}\n"
            )

            # Outcome
            f.write(f"ROW PASSED          : {row['passed']}\n")
            f.write("-" * 70 + "\n\n")

    return str(path)
