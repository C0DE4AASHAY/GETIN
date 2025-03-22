import sqlite3

DB_PATH = "economy.db"

def setup_database():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS log_settings (guild_id INTEGER PRIMARY KEY, log_channel_id INTEGER)")
    conn.commit()
    conn.close()

def set_log_channel(guild_id, channel_id):
    """Set the log channel for a server."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO log_settings (guild_id, log_channel_id) VALUES (?, ?)", (guild_id, channel_id))
    conn.commit()
    conn.close()

def get_log_channel(guild_id):
    """Get the log channel ID for a server."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT log_channel_id FROM log_settings WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
