import sqlite3
import os
 
DB_PATH = os.path.join(os.path.dirname(__file__), "support.db")
 
def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
 
    # Tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id    TEXT PRIMARY KEY,
            status       TEXT DEFAULT "OPEN",
            subject      TEXT,
            assigned_to  TEXT,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
 
    # Escalations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            escalation_id TEXT PRIMARY KEY,
            summary       TEXT,
            category      TEXT,
            priority      TEXT,
            status        TEXT DEFAULT "CREATED",
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
 
    # Cache table — persistent cache for LLM + Pinecone results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            query      TEXT PRIMARY KEY,
            result     TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Conversation history table — stores all messages exchanged with the user
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversation_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT,
            role        TEXT,
            content     TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

 
    # Sample tickets
    tickets = [
        ("TKT-12345","OPEN",  "Login issue reported",    "Support Team A"),
        ("TKT-99887","CLOSED","Billing query resolved",  "Support Team B"),
        ("TKT-55123","OPEN",  "Double charge complaint", "Support Team A"),
        ("TKT-77001","OPEN",  "Password reset failed",   "Support Team C"),
        ("TKT-44332","OPEN",  "App freezing on startup", "Support Team A"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO tickets (ticket_id,status,subject,assigned_to) VALUES (?,?,?,?)",
        tickets
    )
 
    conn.commit()
    conn.close()
    print("✅ Database created: data/support.db")
    print("   Tables: tickets, escalations, cache")
    print("   Sample tickets inserted")
 
if __name__ == "__main__":
    create_tables()
