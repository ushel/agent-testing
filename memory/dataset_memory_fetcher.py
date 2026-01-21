from memory.supabase_client import get_connection

def fetch_dataset_summaries(agent_type: str, limit: int = 10):
    """
    Fetch lightweight dataset summaries filtered by agent_type.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, created_at
        FROM datasets
        WHERE payload->>'agent_type' = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (agent_type, limit)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"dataset_id": r[0], "created_at": r[1]} for r in rows]
