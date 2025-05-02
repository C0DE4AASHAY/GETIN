import sqlite3

# Connect to database (or create if not exists)
conn = sqlite3.connect("economy.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 1000
    )
""")
conn.commit()

def get_balance(user_id):
    """Fetch user's balance from the database."""
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

def update_balance(user_id, amount):
    """Update user's balance (add or subtract)."""
    current_balance = get_balance(user_id)
    new_balance = current_balance + amount

    cursor.execute("""
        INSERT INTO users (user_id, balance) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET balance = excluded.balance
    """, (user_id, new_balance))
    conn.commit()

def set_log_channel(guild_id, channel_id):
    conn = sqlite3.connect("economy.db")  # Apni database file ka naam check karo
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS log_channels (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)")
    cursor.execute("INSERT OR REPLACE INTO log_channels (guild_id, channel_id) VALUES (?, ?)", (guild_id, channel_id))
    conn.commit()
    conn.close()

def get_log_channel(guild_id):
    conn = sqlite3.connect("economy.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM log_channels WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None