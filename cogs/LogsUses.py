import nextcord
from nextcord.ext import commands
from datetime import datetime

class LogsUses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='logs')
    async def MusicUses(self, ctx):
        # server_name = ctx.guild.name if ctx.guild else "Unknown Server"
        embed = nextcord.Embed(
            title='',
            description=''
            '>>>> **For Setup Logs**  <<<<\n\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-sl < Channel ID >`\n\n'
                        '*Note: Mention the Channel ID in which you have to setup Logs*',
            color=0x00ff00
        )

        # Calculate the bot's uptime
        uptime = datetime.utcnow() - self.bot.start_time

        # Set the footer with the formatted uptime
        #embed.set_footer(text=f'Made by asklord • {str(uptime)}')

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(LogsUses(bot))