import discord
from discord.ext import commands
from discord import app_commands
import datetime
import asyncio
import json
import os

SETTINGS_FILE = "spam_protection_settings.json"

class SpamProtectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_message_count = {}
        self.spam_timeout = set()
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return {"enabled": True}
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f)

    @property
    def spam_protection_enabled(self):
        return self.settings.get("enabled", True)

    @spam_protection_enabled.setter
    def spam_protection_enabled(self, value):
        self.settings["enabled"] = value
        self.save_settings()

    async def check_spam(self, message):
        if not self.spam_protection_enabled or not message.guild:
            return

        user_id = message.author.id
        current_time = datetime.datetime.utcnow()

        if user_id in self.user_message_count:
            time_diff = current_time - self.user_message_count[user_id]['last_message_time']
            if time_diff.total_seconds() < 5:
                self.user_message_count[user_id]['message_count'] += 1
                if self.user_message_count[user_id]['message_count'] > 5 and user_id not in self.spam_timeout:
                    if message.author.guild_permissions.administrator:
                        embed = discord.Embed(
                            title="⚠️ Spam Notice (Admin)",
                            description=f"{message.author.mention}, you're sending messages quickly, but you're exempt as an admin.",
                            color=0xFFD700
                        )
                        await message.channel.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title="🚫 Spam Detected",
                            description=f"{message.author.mention}, you're sending messages too fast! Timeout applied for 15 minutes.",
                            color=0xFF0000
                        )
                        await message.channel.send(embed=embed)
                        await self.timeout_user(message.author)
            else:
                self.user_message_count[user_id] = {'last_message_time': current_time, 'message_count': 1}
        else:
            self.user_message_count[user_id] = {'last_message_time': current_time, 'message_count': 1}

    async def timeout_user(self, user):
        self.spam_timeout.add(user.id)
        try:
            timeout_until = discord.utils.utcnow() + datetime.timedelta(minutes=15)
            await user.edit(timed_out_until=timeout_until, reason="Spam protection timeout")
        except Exception as e:
            print(f"Failed to timeout {user}: {e}")
        await asyncio.sleep(15 * 60)
        self.spam_timeout.remove(user.id)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        await self.check_spam(message)

    # Slash Command: Enable Spam Protection
    @app_commands.command(name="sec_on", description="Enable spam protection")
    async def enable_spam(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        self.spam_protection_enabled = True
        embed = discord.Embed(
            title="✅ Spam Protection",
            description="Spam protection has been **enabled**.",
            color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

    # Slash Command: Disable Spam Protection
    @app_commands.command(name="sec_off", description="Disable spam protection")
    async def disable_spam(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        self.spam_protection_enabled = False
        embed = discord.Embed(
            title="❌ Spam Protection",
            description="Spam protection has been **disabled**.",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed)

    # Slash Command: Status of Spam Protection
    @app_commands.command(name="sec_status", description="Show spam protection status")
    async def spam_status(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        status = "🟢 Enabled" if self.spam_protection_enabled else "🔴 Disabled"
        embed = discord.Embed(
            title="📊 Spam Protection Status",
            description=f"Current spam protection is: **{status}**",
            color=0xFFFF00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # async def cog_load(self):
        # Register all slash commands when cog is loaded
        # self.bot.tree.add_command(self.enable_spam)
        # self.bot.tree.add_command(self.disable_spam)
        # self.bot.tree.add_command(self.spam_status)

async def setup(bot):
    await bot.add_cog(SpamProtectionCog(bot))
