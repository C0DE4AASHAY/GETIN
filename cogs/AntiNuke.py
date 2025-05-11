import discord
from discord.ext import commands

class AntiBotNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # IDs of trusted bots that are allowed to stay in the server    
        self.whitelisted_ids = [1069222986751676497]  # Replace with your bot IDs

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # If the new member is a bot and not in the whitelist
        if member.bot and member.id not in self.whitelisted_ids:
            try:
                await member.ban(reason="Untrusted bot detected - AntiNuke System")
                log_channel = discord.utils.get(member.guild.text_channels, name="anti-nuke-logs")
                if log_channel:
                    await log_channel.send(f"🚨 **Untrusted Bot Banned:** `{member}` was automatically banned for anti-nuke protection.")
            except Exception as e:
                print(f"Error banning bot: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # If a bot was given dangerous permissions after joining
        if after.bot and not before.bot:
            for role in after.roles:
                perms = role.permissions
                if perms.administrator or perms.ban_members or perms.manage_roles:
                    try:
                        await after.ban(reason="Bot granted dangerous permissions - AntiNuke System")
                        log_channel = discord.utils.get(after.guild.text_channels, name="anti-nuke-logs")
                        if log_channel:
                            await log_channel.send(f"⚠️ **Bot Banned:** `{after}` was banned for getting dangerous permissions.")
                    except Exception as e:
                        print(f"Error banning bot with perms: {e}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def whitelistbot(self, ctx, bot_id: int):
        """Add a bot to the trusted whitelist."""
        if bot_id not in self.whitelisted_ids:
            self.whitelisted_ids.append(bot_id)
            await ctx.send(f"✅ Bot with ID `{bot_id}` added to whitelist.")
        else:
            await ctx.send("⚠️ That bot is already whitelisted.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removewhitelistbot(self, ctx, bot_id: int):
        """Remove a bot from the trusted whitelist."""
        if bot_id in self.whitelisted_ids:
            self.whitelisted_ids.remove(bot_id)
            await ctx.send(f"🗑️ Bot with ID `{bot_id}` removed from whitelist.")
        else:
            await ctx.send("⚠️ That bot was not in the whitelist.")


async def setup(bot):
    await bot.add_cog(AntiBotNuke(bot))
