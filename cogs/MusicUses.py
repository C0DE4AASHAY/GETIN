import discord
from discord.ext import commands

class MusicUses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='music')
    async def music_help(self, ctx):
        """Displays the music commands dashboard."""
        embed = discord.Embed(
            title='🎵 Music Dashboard',
            description=(
                '>>> **Join a Voice Channel before using these commands:**\n\n'
                '<a:A_arrow_arrow:1190713832860037272> `/play <song name>` — Play a song.\n\n'
                '<a:A_arrow_arrow:1190713832860037272> `/pause` — Pause the current song.\n\n'
                '<a:A_arrow_arrow:1190713832860037272> `/resume` — Resume the paused song.\n\n'
                '<a:A_arrow_arrow:1190713832860037272> `/queue` — View the song queue.\n\n'
                '<a:A_arrow_arrow:1190713832860037272> `/skip` — Skip the current song.\n\n'
                '<a:A_arrow_arrow:1190713832860037272> `/leave` — Disconnect the bot from VC.\n\n'
            ),
            color=0x00ff00
        )

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(MusicUses(bot))

