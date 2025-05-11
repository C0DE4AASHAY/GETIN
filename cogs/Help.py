import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button
from datetime import datetime


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = datetime.utcnow()

    def generate_help_embed(self, server_name: str) -> discord.Embed:
        embed = discord.Embed(
            title='📊 GeTiN Dashboard',
            description=(
                f"**Server Name:** `{server_name}`\n\n"
                "<a:A_arrow_arrow:1190713832860037272> `/mods` — **Show Moderators**\n"
                "<a:A_arrow_arrow:1190713832860037272> `/backup_create` — **Create and Load backups**\n"
                "<a:A_arrow_arrow:1190713832860037272> `/logs` — **Bot Logs**\n"
                "<a:A_arrow_arrow:1190713832860037272> `-fun` — **Fun Commands**\n"
                "<a:A_arrow_arrow:1190713832860037272> `-music` — **Music Commands** *(Working On...)*\n"
                "<a:A_arrow_arrow:1190713832860037272> `-sec` — **Security Options**\n"
                "<a:A_arrow_arrow:1190713832860037272> `-info` — **Server Information**\n"
                # "<a:A_arrow_arrow:1190713832860037272> `/games` — **Games to play** *(Coming Soon...)*\n"

            ),
            color=discord.Color.green()
        )

        # uptime = datetime.utcnow() - self.bot.start_time
        # formatted_uptime = str(uptime).split('.')[0]
        # embed.set_footer(text=f"🟢 Uptime: {formatted_uptime}")
        embed.set_image(url="https://media.giphy.com/media/xUPGGDNsLvqsBOhuU0/giphy.gif")
        return embed

    def generate_invite_button(self) -> View:
        button = Button(
            style=discord.ButtonStyle.link,
            label="🤖 Invite GeTiN",
            url="https://discord.com/oauth2/authorize?client_id=1069222986751676497&scope=bot+applications.commands&permissions=8"
        )
        view = View()
        view.add_item(button)
        return view
    
    @commands.command(name="help")
    async def prefix_help(self, ctx):
        embed = self.generate_help_embed(ctx.guild.name)
        view = self.generate_invite_button()
        await ctx.send(embed=embed, view=view)





    # 🔁 Slash command version of help
    @app_commands.command(name="help", description="Show the GeTiN command dashboard")
    async def slash_help(self, interaction: Interaction):
        embed = self.generate_help_embed(interaction.guild.name if interaction.guild else "Direct Messages")
        view = self.generate_invite_button()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
