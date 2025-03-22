import nextcord
from nextcord.ext import commands

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        # Create an embed message
        embed = nextcord.Embed(
            title="",
            description=f'** Hello {member.mention} Welcome to Our Server.** \n\n' 
            '> **[+] Subscribe Our YouTube channel.**\n'
            '> https://www.youtube.com/@AskLorD0019\n'
            '>  \n'
            '> **[+] Must Join Our Discord Server.**\n'
            '> https://discord.com/GNmbuRBTNf'
            ,
            color=nextcord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url)  # Set the user's avatar as the thumbnail

        try:
            # Send the embed message as a DM to the new member
            await member.send(embed=embed)
        except Exception as e:
            print(f"Failed to send a DM to {member.name}: {e}")

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(WelcomeCog(bot))
