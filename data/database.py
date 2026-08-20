# ─────────────────────────────────────────────────────────
# Database abstraction layer with toggle.
# Change DB_BACKEND to switch between SQLite and Supabase.
# All other code stays completely unchanged.
# ─────────────────────────────────────────────────────────
 
import os
import json
import sqlite3
from dotenv import load_dotenv, find_dotenv
 
load_dotenv(find_dotenv(), override=True)
 
# ── TOGGLE — change this one line to switch databases ────
DB_BACKEND = "supabase"      # ← "sqlite" or "supabase"
# ─────────────────────────────────────────────────────────
 
SQLITE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "support.db"
)
 
# Initialize Supabase client only if needed
_supabase_client = None
 
def get_supabase():
    """Lazy initialize Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        _supabase_client = create_client(url, key)
    return _supabase_client
 
 
# ── TICKETS ─────────────────────────────────────────────
 
def get_ticket(ticket_id: str) -> dict:
    """Get a ticket by ID — works with SQLite or Supabase."""
 
    if DB_BACKEND == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return {"ticket_id": ticket_id, "status": "NOT_FOUND",
                "message": f"Ticket {ticket_id} not found."}
 
    elif DB_BACKEND == "supabase":
        result = get_supabase().table("tickets") \
                               .select("*") \
                               .eq("ticket_id", ticket_id) \
                               .execute()
        if result.data:
            return result.data[0]
        return {"ticket_id": ticket_id, "status": "NOT_FOUND",
                "message": f"Ticket {ticket_id} not found."}
 
 
# ── ESCALATIONS ─────────────────────────────────────────
 
def create_escalation_record(eid: str, summary: str,
                              category: str, priority: str) -> bool:
    """Insert escalation record — works with SQLite or Supabase."""
 
    if DB_BACKEND == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO escalations (escalation_id,summary,category,priority) VALUES (?,?,?,?)",
            (eid, summary, category, priority)
        )
        conn.commit()
        conn.close()
        return True
 
    elif DB_BACKEND == "supabase":
        result = get_supabase().table("escalations").insert({
            "escalation_id": eid,
            "summary":       summary,
            "category":      category,
            "priority":      priority,
        }).execute()
        return bool(result.data)
 
 
def get_all_escalations(category: str = None) -> list:
    """Get escalations — works with SQLite or Supabase."""
 
    if DB_BACKEND == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cat = category or "%"
        cursor.execute("SELECT * FROM escalations WHERE category LIKE ?", (cat,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
 
    elif DB_BACKEND == "supabase":
        query = get_supabase().table("escalations").select("*")
        if category:
            query = query.eq("category", category)
        result = query.execute()
        return result.data or []
 
 
# ── TICKETS SEARCH ──────────────────────────────────────
 
def get_tickets(status: str = "ALL", subject: str = "") -> list:
    """Get tickets with optional filters — works with SQLite or Supabase."""
 
    if DB_BACKEND == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if status == "ALL":
            cursor.execute("SELECT * FROM tickets WHERE subject LIKE ?",
                          (f"%{subject}%",))
        else:
            cursor.execute(
                "SELECT * FROM tickets WHERE status=? AND subject LIKE ?",
                (status, f"%{subject}%")
            )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
 
    elif DB_BACKEND == "supabase":
        query = get_supabase().table("tickets").select("*")
        if status != "ALL":
            query = query.eq("status", status)
        if subject:
            query = query.ilike("subject", f"%{subject}%")
        result = query.execute()
        print(f"  [SUPABASE DEBUG] tickets result: {result}")   # ← add this
        print(f"  [SUPABASE DEBUG] data: {result.data}")        # ← add this
        return result.data or []
 
 
# ── CONVERSATION HISTORY ────────────────────────────────
 
def save_message(session_id: str, role: str, content: str):
    """Save message to history — works with SQLite or Supabase."""
 
    if DB_BACKEND == "sqlite":
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversation_history (session_id,role,content) VALUES (?,?,?)",
                (session_id, role, content)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"  [MEMORY] Failed to save: {e}")
 
    elif DB_BACKEND == "supabase":
        try:
            get_supabase().table("conversation_history").insert({
                "session_id": session_id,
                "role":       role,
                "content":    content,
            }).execute()
        except Exception as e:
            print(f"  [MEMORY] Failed to save: {e}")
 
 
def load_history(session_id: str, limit: int = 10) -> list:
    """Load last N messages — works with SQLite or Supabase."""
 
    if DB_BACKEND == "sqlite":
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """SELECT role, content FROM conversation_history
                   WHERE session_id=? ORDER BY id DESC LIMIT ?""",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            conn.close()
            return [{"role": r["role"], "content": r["content"]}
                    for r in reversed(rows)]
        except:
            return []
 
    elif DB_BACKEND == "supabase":
        try:
            result = get_supabase().table("conversation_history") \
                                   .select("role,content") \
                                   .eq("session_id", session_id) \
                                   .order("id", desc=True) \
                                   .limit(limit) \
                                   .execute()
            return list(reversed(result.data or []))
        except:
            return []
 
 
# ── CACHE ───────────────────────────────────────────────
 
def get_cached_result(query: str):
    """Check cache — works with SQLite or Supabase."""
 
    if DB_BACKEND == "sqlite":
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT result FROM cache WHERE query = ?", (query,))
            row = cursor.fetchone()
            conn.close()
            if row:
                print(f"  [CACHE HIT] returning stored result")
                return json.loads(row[0])
            return None
        except:
            return None
 
    elif DB_BACKEND == "supabase":
        try:
            result = get_supabase().table("cache") \
                                   .select("result") \
                                   .eq("query", query) \
                                   .execute()
            if result.data:
                print(f"  [CACHE HIT] returning stored result")
                return json.loads(result.data[0]["result"])
            return None
        except:
            return None
 
 
def save_to_cache(query: str, result: list):
    """Save to cache — works with SQLite or Supabase."""
 
    if DB_BACKEND == "sqlite":
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO cache (query, result) VALUES (?, ?)",
                (query, json.dumps(result))
            )
            conn.commit()
            conn.close()
        except:
            pass
 
    elif DB_BACKEND == "supabase":
        try:
            get_supabase().table("cache").upsert({
                "query":  query,
                "result": json.dumps(result),
            }).execute()
        except:
            pass
