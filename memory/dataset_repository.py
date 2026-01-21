from memory.supabase_client import get_connection
from psycopg2.extras import Json

def save_dataset(dataset: dict):
    """
    Persist dataset JSON into Postgres (Supabase DB).
    Uses dataset_name as primary key.
    """
    dataset_id = dataset.get("dataset_name")

    if not dataset_id:
        raise ValueError("Dataset missing 'dataset_name'")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO datasets (id, payload)
        VALUES (%s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (dataset_id, Json(dataset))
    )

    conn.commit()
    cur.close()
    conn.close()
