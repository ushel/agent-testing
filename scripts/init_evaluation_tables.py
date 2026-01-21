from memory.supabase_client import get_connection

DDL = """
CREATE TABLE IF NOT EXISTS evaluation_runs (
    id BIGSERIAL PRIMARY KEY,
    dataset_name TEXT,
    agent_type TEXT,
    score FLOAT,
    passed BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evaluation_rows (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT REFERENCES evaluation_runs(id) ON DELETE CASCADE,
    row_index INT,
    prompt TEXT,
    expected_output TEXT,
    actual_output TEXT,
    passed BOOLEAN
);
"""

def main():
    conn = get_connection()
    cur = conn.cursor()

    print("Initializing evaluation tables...")
    cur.execute(DDL)

    conn.commit()
    cur.close()
    conn.close()

    print("Evaluation tables created (or already exist)")

if __name__ == "__main__":
    main()
