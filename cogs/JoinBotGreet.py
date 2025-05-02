import discord
from discord.ext import commands

class Greeting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        inviter = None

        try:
            # Attempt to find who added the bot using audit logs
            async for entry in guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
                inviter = entry.user
                break
        except discord.Forbidden:
            print("Missing permissions to view audit logs.")
        except Exception as e:
            print(f"Error accessing audit logs: {e}")

        if inviter:
            embed = discord.Embed(
                title="Thank You for Inviting Me! 💖",
                description="Use `/help` to explore my features and commands!",
                color=discord.Color.blue()
            )
            embed.set_image(url="https://media.giphy.com/media/xUPGGDNsLvqsBOhuU0/giphy.gif")
            embed.set_footer(text="Excited to be part of your server!")

            try:
                await inviter.send(embed=embed)
                print(f"✅ Greeting sent to {inviter.name}")
            except discord.Forbidden:
                print(f"❌ Couldn't send DM to {inviter.name} (forbidden).")
            except Exception as e:
                print(f"❌ Failed to send DM: {e}")
        else:
            print(f"Joined {guild.name}, but couldn't find who invited me.")

async def setup(bot):
    await bot.add_cog(Greeting(bot))
