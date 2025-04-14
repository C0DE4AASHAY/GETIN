import discord
from discord.ext import commands

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Embed message for welcome
        embed = discord.Embed(
            title=discord.Embed.Empty,
            description=(
                f"**Hello {member.mention}, welcome to our server!**\n\n"
                "> **[+] Subscribe to our YouTube channel:**\n"
                "> https://www.youtube.com/@AskLorD0019\n\n"
                "> **[+] Join our main Discord server:**\n"
                "> https://discord.com/GNmbuRBTNf"
            ),
            color=discord.Color.blue()
        )

        # Set user's avatar or default avatar
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_thumbnail(url=avatar_url)

        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            print(f"❌ Could not send DM to {member.name} (DMs might be disabled).")
        except Exception as e:
            print(f"❌ Failed to send a welcome message to {member.name}: {e}")

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
