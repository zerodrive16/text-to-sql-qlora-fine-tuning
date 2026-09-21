import sqlite3, pathlib 

BASE_DIR = pathlib.Path(__file__).parent.parent # -> brings us to bdataset/
DB_PATH = BASE_DIR / "business.sqlite"
SCHEMA_PATH = BASE_DIR / "schema.sql"

def init_db(): 
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())
    conn.commit()
    conn.close()
    print(f"Created the Database at {DB_PATH}")

if __name__ == "__main__": 
    init_db()