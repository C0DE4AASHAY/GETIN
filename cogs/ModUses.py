import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from datetime import timedelta
import asyncio
from discord.utils import utcnow


class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'start_time'):
            self.bot.start_time = datetime.utcnow()

    def create_embed(self, description, color=discord.Color.green()):
        return discord.Embed(description=description, color=color)

    @app_commands.command(name='mods', description='Show all moderation commands')
    async def security(self, interaction: discord.Interaction):
        server_name = interaction.guild.name if interaction.guild else "Unknown Server"
        embed = discord.Embed(
            title='🛡️ Security Dashboard',
            description=(
                f'**Server name**: **{server_name}**\n\n'
                '<a:A_arrow_arrow:1190713832860037272> **Kick**: `/kick`\n'
                '<a:A_arrow_arrow:1190713832860037272> **Ban**: `/ban`\n'
                '<a:A_arrow_arrow:1190713832860037272> **Unban**: `/unban`\n'
                '<a:A_arrow_arrow:1190713832860037272> **DM Users**: `-dm @user , -dmall`\n'
                '<a:A_arrow_arrow:1190713832860037272> **Add Role**: `/addrole`\n'
                '<a:A_arrow_arrow:1190713832860037272> **Remove Role**: `/rmrole`\n'
                '<a:A_arrow_arrow:1190713832860037272> **Timeout**: `/timeout`\n'
                '<a:A_arrow_arrow:1190713832860037272> **Untimeout**: `/unto`\n'
                '<a:A_arrow_arrow:1190713832860037272> **Delete message**: `/dmsg`\n'
            ),
            color=discord.Color.green()
        )
        uptime = datetime.utcnow() - self.bot.start_time
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ModCog(bot))
