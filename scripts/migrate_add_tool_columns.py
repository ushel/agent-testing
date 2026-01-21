from memory.supabase_client import get_connection

DDL = """
ALTER TABLE evaluation_rows
ADD COLUMN IF NOT EXISTS expected_tools TEXT[],
ADD COLUMN IF NOT EXISTS actual_tools TEXT[],
ADD COLUMN IF NOT EXISTS tool_expected BOOLEAN,
ADD COLUMN IF NOT EXISTS tool_called BOOLEAN,
ADD COLUMN IF NOT EXISTS correct_tool_called BOOLEAN;
"""

def main():
    conn = get_connection()
    cur = conn.cursor()

    print("Running evaluation_rows tool-column migration...")
    cur.execute(DDL)

    conn.commit()
    cur.close()
    conn.close()

    print("Migration completed successfully")

if __name__ == "__main__":
    main()
