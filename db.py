# db.py - Database module for procurement constraints

import sqlite3
from config import DATABASE_PATH, DEFAULT_BUDGET, DEFAULT_DEADLINE


def init_db():
    """Initialize the database with constraints table if not exists."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS constraints (
            id INTEGER PRIMARY KEY,
            budget REAL NOT NULL,
            deadline INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert default constraints if table is empty
    cursor.execute("SELECT COUNT(*) FROM constraints")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO constraints (budget, deadline) VALUES (?, ?)",
            (DEFAULT_BUDGET, DEFAULT_DEADLINE)
        )
    
    conn.commit()
    conn.close()


def get_constraints() -> tuple[float, int]:
    """
    Get budget and deadline constraints from database.
    Returns: (budget, deadline)
    """
    try:
        init_db()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT budget, deadline FROM constraints ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0], result[1]
    except Exception as e:
        print(f"Database error: {e}")
    
    return DEFAULT_BUDGET, DEFAULT_DEADLINE


def update_constraints(budget: float, deadline: int) -> bool:
    """
    Update budget and deadline constraints in database.
    Returns: True if successful
    """
    try:
        init_db()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO constraints (budget, deadline) VALUES (?, ?)",
            (budget, deadline)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False
