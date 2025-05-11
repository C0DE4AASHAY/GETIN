from discord.ext import commands
import discord

class MentionResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            embed = discord.Embed(
                description=f"👋 Hey {message.author.mention}, use </help:0> to explore all features!",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed)

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(MentionResponder(bot))
