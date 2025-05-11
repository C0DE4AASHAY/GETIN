import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
import asyncio
from discord.utils import utcnow

class Mod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def create_embed(self, description: str, color: discord.Color = discord.Color.green()):
        return discord.Embed(description=description, color=color, timestamp=utcnow())

    # ----------------------------------- KICK ----------------------------------- #
    @app_commands.command(name='kick', description='Kick a user from the server')
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member == interaction.user:
            return await interaction.response.send_message(
                embed=self.create_embed("❌ You cannot kick yourself.", discord.Color.red()), ephemeral=True)

        if member == self.bot.user:
            return await interaction.response.send_message(
                embed=self.create_embed("❌ You cannot kick the bot.", discord.Color.red()), ephemeral=True)

        if member.guild_permissions.administrator:
            return await interaction.response.send_message(
                embed=self.create_embed("❌ You cannot kick an administrator.", discord.Color.red()), ephemeral=True)

        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(
                embed=self.create_embed(f"✅ {member.mention} has been kicked.\nReason: `{reason}`"), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                embed=self.create_embed(f"❌ Failed to kick user.\nError: `{e}`", discord.Color.red()), ephemeral=True)

    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(
            embed=self.create_embed("❌ You don't have permission to use this command." if isinstance(error, app_commands.errors.MissingPermissions) else f"⚠️ Error: `{error}`", discord.Color.red()), ephemeral=True)

    # ----------------------------------- BAN ----------------------------------- #
    @app_commands.command(name='ban', description='Ban a user from the server')
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member == interaction.user:
            return await interaction.response.send_message(
                embed=self.create_embed("❌ You cannot ban yourself.", discord.Color.red()), ephemeral=True)

        if member == self.bot.user:
            return await interaction.response.send_message(
                embed=self.create_embed("❌ You cannot ban the bot.", discord.Color.red()), ephemeral=True)

        if member.guild_permissions.administrator:
            return await interaction.response.send_message(
                embed=self.create_embed("❌ You cannot ban an administrator.", discord.Color.red()), ephemeral=True)

        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(
                embed=self.create_embed(f"✅ {member.mention} has been banned.\nReason: `{reason}`"), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                embed=self.create_embed(f"❌ Failed to ban user.\nError: `{e}`", discord.Color.red()), ephemeral=True)

    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(
            embed=self.create_embed("❌ You don't have permission to use this command." if isinstance(error, app_commands.errors.MissingPermissions) else f"⚠️ Error: `{error}`", discord.Color.red()), ephemeral=True)

    # ----------------------------------- UNBAN ----------------------------------- #
    @app_commands.command(name='unban', description='Unban a user by ID')
    @app_commands.checks.has_permissions(administrator=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(
                embed=self.create_embed(f"✅ Unbanned {user.name}"), ephemeral=True)
        except ValueError:
            await interaction.response.send_message(
                embed=self.create_embed("❌ Please enter a valid user ID.", discord.Color.red()), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                embed=self.create_embed(f"❌ Failed to unban user.\nError: `{e}`", discord.Color.red()), ephemeral=True)

    # ----------------------------------- DELETE MESSAGES ----------------------------------- #
    @app_commands.command(name="dmsg", description="Delete a number of messages in this channel.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delete_messages(self, interaction: discord.Interaction, amount: int):
        if amount < 1:
            return await interaction.response.send_message("Please provide a number greater than 0.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        deleted_count = 0

        try:
            while amount > 0:
                to_delete = min(amount, 100)
                deleted = await interaction.channel.purge(limit=to_delete)
                deleted_count += len(deleted)
                amount -= to_delete
                await asyncio.sleep(1)

            await interaction.followup.send(f"🧹 Deleted {deleted_count} messages.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ Missing permission to delete messages.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`", ephemeral=True)

    @app_commands.command(name="dmsg_all", description="Delete all messages in the current channel.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delete_all_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        deleted_count = 0

        try:
            while True:
                deleted = await interaction.channel.purge(limit=100)
                if not deleted:
                    break
                deleted_count += len(deleted)
                await asyncio.sleep(1)

            await interaction.followup.send(f"🧹 Deleted **all** messages ({deleted_count}) in this channel.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ Missing permission to delete messages.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`", ephemeral=True)

    # ----------------------------------- ADD ROLE ----------------------------------- #
    @app_commands.command(name='addrole', description='Add a role to a user')
    @app_commands.checks.has_permissions(manage_roles=True)
    async def addrole(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member):
        try:
            await member.add_roles(role)
            await interaction.response.send_message(
                embed=self.create_embed(f"✅ Added role `{role.name}` to {member.mention}"))
        except Exception as e:
            await interaction.response.send_message(
                embed=self.create_embed(f"❌ Failed to add role: {e}", discord.Color.red()), ephemeral=True)

    # ----------------------------------- REMOVE ROLE ----------------------------------- #
    @app_commands.command(name='rmrole', description='Remove a role from a user')
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rmrole(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member):
        try:
            await member.remove_roles(role)
            await interaction.response.send_message(
                embed=self.create_embed(f"✅ Removed role `{role.name}` from {member.mention}"), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                embed=self.create_embed(f"❌ Failed to remove role: {e}", discord.Color.red()), ephemeral=True)

    # ----------------------------------- DM ONE USER (Prefix) ----------------------------------- #
    @commands.command(name='dm')
    @commands.has_permissions(administrator=True)
    async def dm(self, ctx, user: discord.User, *, message: str):
        try:
            await user.send(message)
            await ctx.send(f"✅ Message sent to {user.name}.")
        except discord.Forbidden:
            await ctx.send(f"❌ Could not send a DM to {user.name}.")
        except discord.HTTPException:
            await ctx.send("⚠️ Failed to send the message.")


# -----------------------------------  TIME OUT USERS  --------------------------------------- #

    @app_commands.command(name='timeout', description='Timeout a user for a given duration (e.g. 10s, 5m, 1h, 1d)')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: str):
        unit = duration[-1]
        try:
            time_val = int(duration[:-1])
        except ValueError:
            return await interaction.response.send_message(embed=self.create_embed("<:Xmark:1360698795171778670> Invalid number format.", discord.Color.red()), ephemeral=True)

        time_dict = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}
        delta = {
            "s": timedelta(seconds=time_val),
            "m": timedelta(minutes=time_val),
            "h": timedelta(hours=time_val),
            "d": timedelta(days=time_val)
        }.get(unit)

        if not delta:
            return await interaction.response.send_message(embed=self.create_embed("<:Xmark:1360698795171778670> Invalid time format. Use s, m, h, or d.", discord.Color.red()), ephemeral=True)

        try:
            await member.edit(timed_out_until=utcnow() + delta)
            await interaction.response.send_message(embed=self.create_embed(f"<:Checkmark:1360698823172686055> {member.mention} has been timed out for {time_val} {time_dict[unit]}"), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=self.create_embed(f"<:Xmark:1360698795171778670> Failed to timeout user: {e}", discord.Color.red()), ephemeral=True)



# -----------------------------------  UN TIME OUT USERS  --------------------------------------- #

    @app_commands.command(name='unto', description='Remove timeout from a user')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unto(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.edit(timed_out_until=None)
            await interaction.response.send_message(embed=self.create_embed(f"<:Checkmark:1360698823172686055> Removed timeout from {member.mention}"), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=self.create_embed(f"<:Xmark:1360698795171778670> Failed to remove timeout: {e}", discord.Color.red()), ephemeral=True)





    # ----------------------------------- DM ALL USERS (Prefix) ----------------------------------- #
    @app_commands.command(name="dmall", description="Send a DM to all non-bot members in the server")
    @app_commands.describe(
        use_embed="Send message as embed or not",
        title="Title of the embed (used only if embed is True)",
        description="Main content of the message",
        footer="Footer of the embed (used only if embed is True)"
    )
    async def dmall(
        self,
        interaction: discord.Interaction,
        use_embed: bool,
        description: str,
        title: str = None,
        footer: str = None
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
            return

        await interaction.response.send_message(f"📩 Sending messages... This may take a while.", ephemeral=True)

        members = [member for member in interaction.guild.members if not member.bot]
        total_success, total_failed = 0, 0
        batch_size = 10

        async def send_dm(member):
            try:
                if use_embed:
                    embed = discord.Embed(
                        title=title or "📢 Announcement",
                        description=description,
                        color=discord.Color.green()
                    )
                    if footer:
                        embed.set_footer(text=footer)
                    await member.send(embed=embed)
                else:
                    await member.send(description)
                return True
            except:
                return False

        for i in range(0, len(members), batch_size):
            batch = members[i:i+batch_size]
            results = await asyncio.gather(*[send_dm(member) for member in batch])
            total_success += results.count(True)
            total_failed += results.count(False)
            await asyncio.sleep(0.1)

        await interaction.followup.send(f"✅ Successfully sent to {total_success} members.\n❌ Failed to send to {total_failed} members.", ephemeral=True)

    @dmall.error
    async def dmall_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.AppCommandError):
            await interaction.response.send_message("❌ An error occurred while processing the command.", ephemeral=True)



    # ----------------------------------- SYNC ----------------------------------- #
    @commands.Cog.listener()
    async def on_ready(self):
        try:
            synced = await self.bot.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands.")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")







async def setup(bot: commands.Bot):
    await bot.add_cog(Mod(bot))
