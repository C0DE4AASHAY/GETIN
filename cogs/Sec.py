import nextcord
from nextcord.ext import commands
from datetime import datetime

class SecCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='sec')
    async def security(self, ctx):
        server_name = ctx.guild.name if ctx.guild else "Unknown Server"
        embed = nextcord.Embed(
            title='Security Dashboard',
            description=f'Server name: **{server_name}**\n\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-ss`: __To check the status of Protocol.__\n\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-es`: __To enable the Spam Protocol.__\n\n'
            '<a:A_arrow_arrow:1190713832860037272> `-ds`: __To disable the Spam Protocol.__\n\n'
            '<a:A_arrow_arrow:1190713832860037272> `-ping`: __To Check Ping.__\n\n',
            color=0x00ff00
        )

        # Calculate the bot's uptime
        uptime = datetime.utcnow() - self.bot.start_time

        # Set the footer with the formatted uptime
        #embed.set_footer(text=f'Made by asklord • {str(uptime)}')

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(SecCog(bot))