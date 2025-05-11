import discord
from discord.ext import commands

class SIU(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='info')  # Removed '-' from the name
    async def music_help(self, ctx):
        """Displays the Server Info commands dashboard."""
        embed = discord.Embed(
            title='Info Dashboard',
            description=(
                '<a:A_arrow_arrow:1190713832860037272> `-si` — Shows the Server information.\n\n'
                '<a:A_arrow_arrow:1190713832860037272> `-ri` — Shows the Role information.\n\n'
            ),
            color=0x00ff00
        )

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SIU(bot))
