import sqlite3
import discord
from discord.ext import commands
from datetime import datetime

DB_PATH = "economy.db"

class LogDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'start_time'):
            self.bot.start_time = datetime.utcnow()

        # Ensure database and tables are initialized
        self.setup_database()

    def setup_database(self):
        """Create the log_settings table if it doesn't exist."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_settings (
                    guild_id INTEGER PRIMARY KEY,
                    log_channel_id INTEGER
                )
            """)
            conn.commit()

    @staticmethod
    def set_log_channel(guild_id, channel_id):
        """Set or update the log channel for a specific guild."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                REPLACE INTO log_settings (guild_id, log_channel_id)
                VALUES (?, ?)
            """, (guild_id, channel_id))
            conn.commit()

    @staticmethod
    def get_log_channel(guild_id):
        """Retrieve the log channel ID for a specific guild."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT log_channel_id FROM log_settings
                WHERE guild_id = ?
            """, (guild_id,))
            result = cursor.fetchone()
            return result[0] if result else None

async def setup(bot):
    await bot.add_cog(LogDB(bot))

