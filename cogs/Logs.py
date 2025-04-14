import discord
from discord.ext import commands
from discord import app_commands
import datetime
from database import set_log_channel, get_log_channel


class BotLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild_id, embed: discord.Embed):
        log_channel_id = get_log_channel(guild_id)
        if log_channel_id:
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)

    @app_commands.command(name="setlogs", description="Set the log channel (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_set_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        set_log_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"✅ **Logs will now be sent to {channel.mention}**", ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ Error: {str(error)}", ephemeral=True)


    @commands.Cog.listener()
    async def on_command(self, ctx):
        embed = discord.Embed(title="📜 Command Used", color=0x3498db)
        embed.add_field(name="Command", value=f"```{ctx.command}```", inline=False)
        embed.add_field(name="User", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.add_field(name="Channel", value=ctx.channel.mention, inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(ctx.guild.id, embed)


    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        if entry.action == discord.AuditLogAction.member_update:
            target = entry.target
            changes = entry.changes

            if not isinstance(target, discord.Member) or not changes:
                return

            # Check for Timeout applied
            if "communication_disabled_until" in changes:
                before = changes["communication_disabled_until"].before
                after = changes["communication_disabled_until"].after

                embed = discord.Embed(
                    title="🔇 Member Timed Out" if after else "🔈 Timeout Removed",
                    color=discord.Color.orange() if after else discord.Color.green(),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(name="User", value=f"{target.mention} ({target.id})", inline=False)
                embed.add_field(name="Moderator", value=f"{entry.user.mention} ({entry.user.id})", inline=False)

                if after:
                    embed.add_field(name="Until", value=discord.utils.format_dt(after, style='F'), inline=False)
                embed.add_field(name="Reason", value=entry.reason or "No reason provided", inline=False)

                await self.send_log(entry.guild.id, embed)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(title="⚠️ Command Error", color=0xe74c3c)
        embed.add_field(name="Command", value=f"```{getattr(ctx.command, 'name', 'Unknown')}```", inline=False)
        embed.add_field(name="Error", value=f"```{error}```", inline=False)
        embed.add_field(name="User", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(ctx.guild.id, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return

        embed = discord.Embed(title="🗑️ Message Deleted", color=0xe67e22)
        embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        if message.content:
            embed.add_field(name="Message", value=f"```{message.content}```", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(message.guild.id, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content or not before.guild:
            return

        embed = discord.Embed(title="✏️ Message Edited", color=0xf1c40f)
        embed.add_field(name="User", value=f"{before.author} ({before.author.id})", inline=False)
        embed.add_field(name="Channel", value=before.channel.mention, inline=False)
        embed.add_field(name="Before", value=f"```{before.content}```", inline=False)
        embed.add_field(name="After", value=f"```{after.content}```", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(before.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        embed = discord.Embed(title="🔄 Member Updated", color=0x1abc9c)

        if before.nick != after.nick:
            embed.add_field(name="Nickname Changed", value=f"**Before:** {before.nick}\n**After:** {after.nick}", inline=False)

        added_roles = [r.mention for r in after.roles if r not in before.roles]
        removed_roles = [r.mention for r in before.roles if r not in after.roles]

        if added_roles:
            embed.add_field(name="✅ Roles Added", value=", ".join(added_roles), inline=False)
        if removed_roles:
            embed.add_field(name="❌ Roles Removed", value=", ".join(removed_roles), inline=False)

        if embed.fields:
            embed.add_field(name="User", value=f"{before} ({before.id})", inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            await self.send_log(after.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(title="🚨 Member Banned", color=0xe74c3c)
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(guild.id, embed)

    @commands.Cog.listener()
    async def on_member_kick(self, guild, user):
        embed = discord.Embed(title="🚨 Member Kicked", color=0xe74c3c)
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(guild.id, embed)


    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(title="✅ Member Unbanned", color=0x2ecc71)
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(guild.id, embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(title="✅ Member Joined", color=0x2ecc71)
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(member.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(title="❌ Member Left", color=0xe74c3c)
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(member.guild.id, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.guild:
            return

        embed = discord.Embed(color=0x3498db, timestamp=datetime.datetime.utcnow())
        description = None

        if before.channel is None and after.channel is not None:
            embed.title = "🔊 Voice Channel Joined"
            description = f"{member.mention} **joined** {after.channel.mention}"
        elif before.channel is not None and after.channel is None:
            embed.title = "🔇 Voice Channel Left"
            description = f"{member.mention} **left** {before.channel.mention}"
        elif before.channel != after.channel:
            embed.title = "🔁 Voice Channel Switched"
            description = f"{member.mention} **moved from** {before.channel.mention} to {after.channel.mention}"

        if description:
            embed.description = description
            embed.set_footer(text=f"User ID: {member.id}")
            await self.send_log(member.guild.id, embed)


async def setup(bot):
    await bot.add_cog(BotLogs(bot))
