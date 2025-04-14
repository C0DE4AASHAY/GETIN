import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from datetime import timedelta
import time
import pytz 
from discord.utils import utcnow

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# -----------------------------------  CHECKING AVATARS USERS  --------------------------------------- #

    @app_commands.command(name='av', description="Get someone's avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.blue())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)



# ------------------------------------- CHECK PINGS --------------------------------------------------- #

    @app_commands.command(name="ping", description="Check your Ping.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)  # Convert to ms
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}ms**",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)




# ------------------------------------- CHECK TIME --------------------------------------------------- #

    @app_commands.command(name="time", description="Check the current time in UTC and Asia/Kolkata")
    async def slash_time(self, interaction: discord.Interaction):
        utc_now = datetime.utcnow()
        india_tz = pytz.timezone("Asia/Kolkata")
        india_now = utc_now.replace(tzinfo=pytz.utc).astimezone(india_tz)

        embed = discord.Embed(
            title="⏰ Current Time",
            color=discord.Color.blue()
        )
        embed.add_field(name="UTC Time 🌍", value=f"`{utc_now.strftime('%Y-%m-%d %H:%M:%S')}`", inline=False)
        embed.add_field(name="India Time 🇮🇳", value=f"`{india_now.strftime('%Y-%m-%d %I:%M:%S %p')}`", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)



async def setup(bot):
    await bot.add_cog(FunCog(bot))
