import nextcord
import asyncio
from nextcord.ext import commands

class DmCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to send a direct message to a specific user
    @commands.command(name='dm')
    @commands.has_permissions(administrator=True)  # Only admins can use this
    async def dm(self, ctx, user: nextcord.User, *, message: str):
        """Sends a private message to a specific user"""
        try:
            await user.send(message)
            await ctx.send(f"✅ Message sent to {user.name}.")
        except nextcord.errors.Forbidden:
            await ctx.send(f"❌ Could not send a DM to {user.name}. They may have DMs disabled.")
        except nextcord.errors.HTTPException:
            await ctx.send("⚠️ An error occurred while sending the message.")

    # High-Speed Bulk DM
    @commands.command(name='dmall')
    @commands.has_permissions(administrator=True)  # Only admins can use this
    async def dmall(self, ctx, *, message: str):
        """Sends a direct message to all users in the server (FAST MODE)"""
        members = [member for member in ctx.guild.members if not member.bot]

        await ctx.send(f"📩 Sending messages to {len(members)} members...")

        async def send_dm(member):
            try:
                await member.send(message)
                return True
            except nextcord.errors.Forbidden:
                return False

        # Process 10 DMs at once using asyncio.gather
        batch_size = 10
        total_success = 0
        total_failed = 0

        for i in range(0, len(members), batch_size):
            batch = members[i:i + batch_size]
            results = await asyncio.gather(*[send_dm(member) for member in batch])
            
            total_success += results.count(True)
            total_failed += results.count(False)

            await asyncio.sleep(0.01)  # 10ms delay for batches

        await ctx.send(f"✅ Successfully sent DMs to {total_success} users.\n❌ Failed to send to {total_failed} users (DMs disabled).")

def setup(bot):
    bot.add_cog(DmCog(bot))
