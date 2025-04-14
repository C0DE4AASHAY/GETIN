import discord
from discord.ext import commands
from datetime import datetime

class FunUsesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='fun')
    async def security(self, ctx):
        server_name = ctx.guild.name if ctx.guild else "Unknown Server"

        embed = discord.Embed(
            title='Fun Commands Dashboard',
            description=(
                '<a:A_arrow_arrow:1190713832860037272> `/ping`: To check bot latency.\n'
                '<a:A_arrow_arrow:1190713832860037272> `/av @user   `: To check avatar of any user.\n' \
                '<a:A_arrow_arrow:1190713832860037272> `/time`: To check the current time.\n'
            ),
            color=0x00ff00
        )

        # # Get uptime if available
        # if hasattr(self.bot, 'start_time'):
        #     uptime = datetime.utcnow() - self.bot.start_time
        #     uptime_str = str(uptime).split('.')[0]  # Clean uptime display (remove microseconds)
        #     embed.set_footer(text=f'🕒 Bot Uptime: {uptime_str}')
        # else:
        #     embed.set_footer(text='🛠️ Made by asklord')

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FunUsesCog(bot))



