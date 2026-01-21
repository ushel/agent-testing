# --------------------------------------------------
# Evaluation Repository (Supabase / Postgres)
# --------------------------------------------------

import psycopg2
from memory.supabase_client import get_connection


def save_evaluation(
    dataset_name: str,
    agent_type: str,
    score: float,
    passed: bool,
    row_results: list
):
    """
    Persist evaluation run and row-level results.

    Tool usage is stored explicitly.
    """

    conn = get_connection()
    cur = conn.cursor()

    # --------------------------------------------------
    # 1️⃣ Insert evaluation run
    # --------------------------------------------------
    cur.execute(
        """
        INSERT INTO evaluation_runs (
            dataset_name,
            agent_type,
            score,
            passed
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (dataset_name, agent_type, score, passed)
    )

    run_id = cur.fetchone()[0]

    # --------------------------------------------------
    # 2️⃣ Insert row-level evaluation results
    # --------------------------------------------------
    for row in row_results:
        cur.execute(
            """
            INSERT INTO evaluation_rows (
                run_id,
                row_index,
                prompt,
                expected_output,
                actual_output,

                expected_tools,
                actual_tools,
                tool_expected,
                tool_called,
                correct_tool_called,

                passed
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s
            )
            """,
            (
                run_id,
                row["row_index"],
                row["prompt"],
                row["expected_output"],
                row["actual_output"],

                row.get("expected_tools", []),
                row.get("actual_tools", []),
                row.get("tool_expected", False),
                row.get("tool_called", False),
                row.get("correct_tool_called", False),

                row["passed"]
            )
        )

    conn.commit()
    cur.close()
    conn.close()

    return run_id
