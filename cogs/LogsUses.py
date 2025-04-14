import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class LogsUses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'start_time'):
            self.bot.start_time = datetime.utcnow()

    @app_commands.command(name='logs', description='Show how to set up logs for the bot')
    async def show_logs_help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title='📝 Logs Setup Instructions',
            description=(
                '>>>> **For Setup Logs** <<<<\n\n'
                '<a:A_arrow_arrow:1190713832860037272> `/setlogs <channel>`\n\n'
                '*Note: Mention the channel where you want to set up logs.*'
            ),
            color=discord.Color.green()
        )

        # Calculate bot uptime
        uptime = datetime.utcnow() - self.bot.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        embed.set_footer(
            text=f"Uptime: {hours}h {minutes}m {seconds}s • Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LogsUses(bot))
