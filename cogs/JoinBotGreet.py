import nextcord
from nextcord.ext import commands

class Greeting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        inviter = None
        
        # Try to find the inviter from audit logs
        async for entry in guild.audit_logs(action=nextcord.AuditLogAction.bot_add, limit=1):
            inviter = entry.user
            break

        if inviter is not None:
            embed = nextcord.Embed(
                title="Thank You for Inviting Me!",
                description="Get More info it by just typing `-help`",
                color=nextcord.Color.blue()
            )
            embed.set_image(url="https://images-ext-1.discordapp.net/external/mJ9-7nxOuBgiFSDfyvyxfQmGZN1CA5PSpwaLc3DUh-4/https/media.giphy.com/media/xUPGGDNsLvqsBOhuU0/giphy.gif")  # Add your desired GIF URL here
            
            try:
                await inviter.send(embed=embed)
                print(f"Greeting sent to {inviter.name}")
            except nextcord.Forbidden:
                print(f"Couldn't send DM to {inviter.name}")

def setup(bot):
    bot.add_cog(Greeting(bot))
