import nextcord
import time
from nextcord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Advanced Ping Command with Latency Breakdown"""
        
        # Get API Latency (WebSocket)
        ws_latency = round(self.bot.latency * 1000, 2)

        # Record start time
        start_time = time.perf_counter()
        
        # Send a temporary message
        msg = await ctx.send("Pinging...")
        
        # Measure message latency
        msg_latency = round((time.perf_counter() - start_time) * 1000, 2)

        # Embed Response
        embed = nextcord.Embed(
            title="🏓 Pong!",
            color=nextcord.Color.green()
        )
        embed.add_field(name="💡 Bot Latency", value=f"`{msg_latency}ms`", inline=False)
        embed.add_field(name="🔗 WebSocket Latency (API)", value=f"`{ws_latency}ms`", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

        # Edit the message with latency details
        await msg.edit(content=None, embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))



# import nextcord
# from nextcord.ext import commands

# class PingCog(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @nextcord.slash_command(name="ping", description="Check bot latency")
#     async def ping(self, interaction: nextcord.Interaction):
#         await interaction.response.defer()  # Ensures bot responds instantly (prevents timeout)
#         latency = round(self.bot.latency * 1000, 2)
#         await interaction.followup.send(f"Pong! 🏓 Latency: {latency}ms")  # Sends actual message

# def setup(bot):
#     bot.add_cog(PingCog(bot))
