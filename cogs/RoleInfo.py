import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime
from typing import Optional

class RoleInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roleinfo", aliases=["ri"])
    @commands.guild_only()
    async def role_info(self, ctx, *, role: Optional[discord.Role] = None):
        if not role:
            await ctx.send("Please mention a role or provide its name!")
            return

        members = [m for m in ctx.guild.members if role in m.roles]
        bots = [m for m in members if m.bot]
        humans = [m for m in members if not m.bot]
        online = sum(m.status != discord.Status.offline for m in members)

        embed = discord.Embed(
            title=f"📊 Role Information: {role.name}",
            color=role.color,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="🆔 Role ID", value=f"`{role.id}`", inline=True)
        embed.add_field(name="🎨 Color", value=f"`{str(role.color)}`", inline=True)
        embed.add_field(name="📅 Created", value=discord.utils.format_dt(role.created_at, 'R'), inline=True)
        embed.add_field(name="📌 Position", value=f"{role.position} (from bottom)", inline=True)
        embed.add_field(name="👑 Hoisted", value="✅" if role.hoist else "❌", inline=True)
        embed.add_field(name="💳 Mentionable", value="✅" if role.mentionable else "❌", inline=True)
        embed.add_field(
            name=f"👥 Members ({len(members)})",
            value=f"• Humans: {len(humans)}\n• Bots: {len(bots)}\n• Online: {online}",
            inline=False
        )

        perms = []
        p = role.permissions
        if p.administrator: perms.append("Administrator")
        if p.manage_guild: perms.append("Manage Server")
        if p.ban_members: perms.append("Ban Members")
        if p.kick_members: perms.append("Kick Members")
        if p.manage_roles: perms.append("Manage Roles")
        if p.manage_channels: perms.append("Manage Channels")

        embed.add_field(name="🔑 Key Permissions", value=", ".join(perms) if perms else "No special permissions", inline=False)

        view = RoleMembersView(ctx.author, role, members)
        view.message = await ctx.send(embed=embed, view=view)

class RoleMembersView(View):
    def __init__(self, author, role, members):
        super().__init__(timeout=60)
        self.author = author
        self.role = role
        self.members = sorted(members, key=lambda m: m.joined_at or datetime.min)
        self.current_page = 0
        self.per_page = 10
        self.total_pages = max((len(self.members) - 1) // self.per_page + 1, 1)
        self.message = None

    def get_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_members = self.members[start:end]

        embed = discord.Embed(
            title=f"👥 Members with {self.role.name} Role",
            description=f"Page {self.current_page + 1}/{self.total_pages}",
            color=self.role.color
        )

        lines = []
        for i, m in enumerate(page_members, start=start + 1):
            lines.append(
                f"**{i}.** {m.mention} ({m})\n"
                f"• Joined: {discord.utils.format_dt(m.joined_at, 'R') if m.joined_at else 'Unknown'}\n"
                f"• Created: {discord.utils.format_dt(m.created_at, 'R')}"
            )

        embed.add_field(name=f"Total Members: {len(self.members)}", value="\n\n".join(lines), inline=False)
        embed.set_footer(text=f"Role ID: {self.role.id}")
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Only the command author can use these buttons.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="➡️ Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass

async def setup(bot):
    await bot.add_cog(RoleInfo(bot))
