import nextcord
from nextcord.ext import commands
import datetime
from database import set_log_channel, get_log_channel  # Database functions for storing log channel IDs

class BotLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild_id, embed: nextcord.Embed):
        """Send log messages to the stored log channel."""
        log_channel_id = get_log_channel(guild_id)
        if log_channel_id:
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)

    @commands.command(name="setlogs", aliases=["sl"])
    @commands.has_permissions(administrator=True)
    async def set_logs_channel(self, ctx, channel: nextcord.TextChannel):
        """Set the log channel (Admin only)."""
        set_log_channel(ctx.guild.id, channel.id)
        await ctx.send(f"✅ **Logs will now be sent to {channel.mention}**")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Log when a command is used."""
        embed = nextcord.Embed(title="📜 Command Used", color=0x3498db)
        embed.add_field(name="Command", value=f"```{ctx.command}```", inline=False)
        embed.add_field(name="User", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.add_field(name="Channel", value=f"{ctx.channel.mention}", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(ctx.guild.id, embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Log when a command throws an error."""
        embed = nextcord.Embed(title="⚠️ Command Error", color=0xe74c3c)
        embed.add_field(name="Command", value=f"```{ctx.command}```", inline=False)
        embed.add_field(name="Error", value=f"```{error}```", inline=False)
        embed.add_field(name="User", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(ctx.guild.id, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log deleted messages."""
        if message.author.bot:
            return

        embed = nextcord.Embed(title="🗑️ Message Deleted", color=0xe67e22)
        embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
        embed.add_field(name="Channel", value=f"{message.channel.mention}", inline=False)
        if message.content:
            embed.add_field(name="Message", value=f"```{message.content}```", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(message.guild.id, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log edited messages."""
        if before.author.bot or before.content == after.content:
            return

        embed = nextcord.Embed(title="✏️ Message Edited", color=0xf1c40f)
        embed.add_field(name="User", value=f"{before.author} ({before.author.id})", inline=False)
        embed.add_field(name="Channel", value=f"{before.channel.mention}", inline=False)
        embed.add_field(name="Before", value=f"```{before.content}```", inline=False)
        embed.add_field(name="After", value=f"```{after.content}```", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(before.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Log nickname changes and role updates."""
        embed = nextcord.Embed(title="🔄 Member Updated", color=0x1abc9c)

        if before.nick != after.nick:
            embed.add_field(name="Nickname Changed", value=f"**Before:** {before.nick}\n**After:** {after.nick}", inline=False)

        added_roles = [r.mention for r in after.roles if r not in before.roles]
        removed_roles = [r.mention for r in before.roles if r not in after.roles]

        if added_roles:
            embed.add_field(name="✅ Roles Added", value=", ".join(added_roles), inline=False)
        if removed_roles:
            embed.add_field(name="❌ Roles Removed", value=", ".join(removed_roles), inline=False)

        if before.nick != after.nick or added_roles or removed_roles:
            embed.add_field(name="User", value=f"{before} ({before.id})", inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            await self.send_log(after.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Log when a user gets banned."""
        embed = nextcord.Embed(title="🚨 Member Banned", color=0xe74c3c)
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(guild.id, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Log when a user gets unbanned."""
        embed = nextcord.Embed(title="✅ Member Unbanned", color=0x2ecc71)
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(guild.id, embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log when a user joins the server."""
        embed = nextcord.Embed(title="✅ Member Joined", color=0x2ecc71)
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(member.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log when a user leaves the server."""
        embed = nextcord.Embed(title="❌ Member Left", color=0xe74c3c)
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.send_log(member.guild.id, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Log when a user joins, leaves, or switches voice channels."""
        embed = nextcord.Embed(color=0x3498db, timestamp=datetime.datetime.utcnow())

        if before.channel is None and after.channel is not None:
            embed.title = "🔊 Voice Channel Joined"
            embed.description = f"{member.mention} **joined** {after.channel.mention}"

        elif before.channel is not None and after.channel is None:
            embed.title = "🔇 Voice Channel Left"
            embed.description = f"{member.mention} **left** {before.channel.mention}"

        elif before.channel != after.channel:
            embed.title = "🔁 Voice Channel Switched"
            embed.description = f"{member.mention} **moved from** {before.channel.mention} **to** {after.channel.mention}"

        if embed.description:
            embed.set_footer(text=f"User ID: {member.id}")
            await self.send_log(member.guild.id, embed)

def setup(bot):
    bot.add_cog(BotLogs(bot))
