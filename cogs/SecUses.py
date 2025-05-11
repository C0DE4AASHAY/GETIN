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
                '<a:A_arrow_arrow:1190713832860037272> `/sec_status`: __To check the status of the Spam Protocol.__\n'
                '<a:A_arrow_arrow:1190713832860037272> `/sec_on`: __To enable the Spam Protocol.__\n'
                '<a:A_arrow_arrow:1190713832860037272> `/sec_off`: __To disable the Spam Protocol.__\n'
            ),
            color=0x00ff00
        )

        # Get uptime if available
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SecCog(bot))



