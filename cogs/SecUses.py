import discord
from discord.ext import commands
from datetime import datetime

class SecCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='sec')
    async def security(self, ctx):
        server_name = ctx.guild.name if ctx.guild else "Unknown Server"

        embed = discord.Embed(
            title='🛡️ Security Dashboard',
            description=(
                f'**Server:** `{server_name}`\n\n'
                '<a:A_arrow_arrow:1190713832860037272> `/ss`: __To check the status of the Spam Protocol.__\n'
                '<a:A_arrow_arrow:1190713832860037272> `/es`: __To enable the Spam Protocol.__\n'
                '<a:A_arrow_arrow:1190713832860037272> `/ds`: __To disable the Spam Protocol.__\n'
            ),
            color=0x00ff00
        )

        # Get uptime if available
        if hasattr(self.bot, 'start_time'):
            uptime = datetime.utcnow() - self.bot.start_time
            uptime_str = str(uptime).split('.')[0]  # Clean uptime display (remove microseconds)
            embed.set_footer(text=f'🕒 Bot Uptime: {uptime_str}')
        else:
            embed.set_footer(text='🛠️ Made by asklord')

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SecCog(bot))



