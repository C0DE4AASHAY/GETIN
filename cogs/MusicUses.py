import nextcord
from nextcord.ext import commands
from datetime import datetime

class MusicUses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='music')
    async def MusicUses(self, ctx):
        # server_name = ctx.guild.name if ctx.guild else "Unknown Server"
        embed = nextcord.Embed(
            title='Music Dashboard',
            description=''
            '>>>> **Join in Voice Channel**  <<<<\n\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-join`\n\n'
                        '<a:A_arrow_arrow:1190713832860037272> `-play <Song name>`\n\n'
            '<a:A_arrow_arrow:1190713832860037272> `-pause` \n\n'
            '<a:A_arrow_arrow:1190713832860037272> `-resume`\n\n'
            '<a:A_arrow_arrow:1190713832860037272> `-queue`\n\n'
            '<a:A_arrow_arrow:1190713832860037272> `-skip`\n\n'
            '<a:A_arrow_arrow:1190713832860037272> `-leave`\n\n',
            color=0x00ff00
        )

        # Calculate the bot's uptime
        uptime = datetime.utcnow() - self.bot.start_time

        # Set the footer with the formatted uptime
        #embed.set_footer(text=f'Made by asklord • {str(uptime)}')

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MusicUses(bot))