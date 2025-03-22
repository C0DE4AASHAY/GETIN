import nextcord
from nextcord.ext import commands
import asyncio

class DeleteMessageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dmsg')
    @commands.has_permissions(manage_messages=True)
    async def delete_messages(self, ctx, amount: int):
        if amount < 1:
            await ctx.send("Please specify a positive number of messages to delete.")
            return

        try:
            # Log the attempt to delete messages
            print(f"Attempting to delete {amount} messages in {ctx.channel.name}.")

            # Batch delete messages in chunks of 100 to avoid rate limits
            deleted_count = 0
            while amount > 0:
                to_delete = min(amount, 100)  # Discord API allows up to 100 messages at a time
                deleted_messages = await ctx.channel.purge(limit=to_delete)
                deleted_count += len(deleted_messages)
                amount -= len(deleted_messages)

                # Log the number of messages actually deleted in this batch
                print(f"Deleted {len(deleted_messages)} messages in {ctx.channel.name}.")

                # Small delay to avoid rate limits
                await asyncio.sleep(1)

            await ctx.send(f"Deleted {deleted_count} messages.", delete_after=5)
        except nextcord.Forbidden:
            await ctx.send("I don't have permission to delete messages.")
        except nextcord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(DeleteMessageCog(bot))
