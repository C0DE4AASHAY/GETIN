import nextcord
from nextcord.ext import commands
from nextcord.ui import View, Button
from datetime import datetime

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = datetime.utcnow()  # Ensure start time is set

    @commands.command(name='help')
    async def help_panel(self, ctx):
        server_name = ctx.guild.name if ctx.guild else "Unknown Server"
        embed = nextcord.Embed(
            title='GeTiN Dashboard',
            description=f'**Server name: {server_name}**\n\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-mods`: **Show Moderators**\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-sec`: **Security Options**\n'
                        #baad me banaunga <a:A_arrow_arrow:1190713832860037272> **`-modify`**: **`Modify this bot`**\n
                        '<a:A_arrow_arrow:1190713832860037272> `-games`: **Games to play**\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-music`: **Music Commands**\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-fun`: **Fun Commands** (Comming Soon...)\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-utility`: **Utility Commands** (Comming Soon...)\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-logs`: **Bot Logs**\n',
            color=0x00ff00
        )

        # Calculate the bot's uptime
        uptime = datetime.utcnow() - self.bot.start_time

        gif_url = 'https://media.giphy.com/media/xUPGGDNsLvqsBOhuU0/giphy.gif'
        embed.set_image(url=gif_url)

        # Add invite button
        invite_button = Button(style=nextcord.ButtonStyle.link, label="Invite GeTiN", url="https://discord.com/oauth2/authorize?client_id=1069222986751676497&scope=bot&permissions=2171600904")
        view = View()
        view.add_item(invite_button)

        await ctx.send(embed=embed, view=view)

def setup(bot):
    bot.add_cog(HelpCog(bot))
