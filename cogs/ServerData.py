import discord
from discord.ext import commands
from datetime import datetime
from discord.ui import Button, View

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_server_stats(self, guild):
        await guild.chunk(cache=True)  # Ensure all members are cached
        members = guild.members
        bots = [m for m in members if m.bot]
        humans = [m for m in members if not m.bot]
        online = sum(m.status != discord.Status.offline for m in members if not m.bot)

        return {
            'total_members': len(members),
            'humans': len(humans),
            'bots': len(bots),
            'online': online,
            'roles': sorted(
                [r for r in guild.roles if r != guild.default_role],
                key=lambda r: len(r.members),
                reverse=True
            )
        }

    async def create_main_embed(self, ctx, stats):
        guild = ctx.guild
        embed = discord.Embed(
            title=f"📊 Server Info - {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        try:
            owner = guild.get_member(guild.owner_id) or await guild.fetch_member(guild.owner_id)
            embed.add_field(name="👑 Owner", value=f"{owner.mention} ({owner})", inline=False)
        except:
            embed.add_field(name="👑 Owner", value="Could not fetch owner", inline=False)

        embed.add_field(
            name="📅 Created",
            value=f"{guild.created_at.strftime('%d %b %Y')}\n({discord.utils.format_dt(guild.created_at, 'R')})",
            inline=False
        )

        embed.add_field(name="👥 Members", value=f"""
Total: {stats['total_members']:,}
Humans: {stats['humans']:,}
Bots: {stats['bots']:,}
Online: {stats['online']:,}
""", inline=True)

        embed.add_field(name="📚 Channels", value=f"""
Text: {len(guild.text_channels):,}
Voice: {len(guild.voice_channels):,}
Categories: {len(guild.categories):,}
""", inline=True)

        embed.add_field(name="⚙️ Settings", value=f"""
Verification: {str(guild.verification_level).title()}
Boosts: {guild.premium_subscription_count:,} (Tier {guild.premium_tier})
""", inline=False)

        embed.set_footer(
            text=f"Page 1/{(len(stats['roles']) - 1)//10 + 1} • Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )
        return embed

    async def create_roles_embed(self, ctx, stats, page):
        guild = ctx.guild
        roles = stats['roles']
        roles_per_page = 10
        total_pages = max((len(roles) - 1) // roles_per_page + 1, 1)

        start = (page - 1) * roles_per_page
        end = start + roles_per_page
        current_roles = roles[start:end]

        embed = discord.Embed(
            title=f"🎭 Roles in {guild.name} (Page {page}/{total_pages})",
            description=f"Total roles: {len(roles):,}",
            color=discord.Color.green()
        )

        for role in current_roles:
            color_display = f"#{role.color.value:06X}" if role.color.value != 0 else "Default"
            embed.add_field(
                name=f"{str(role)} ({len(role.members):,} members)",
                value=f"Position: {role.position}\nColor: {color_display}",
                inline=True
            )

        embed.set_footer(
            text=f"Role information • {len(roles)} total roles",
            icon_url=guild.icon.url if guild.icon else None
        )
        return embed

    @commands.command(name="serverinfo", aliases=["si"])
    @commands.guild_only()
    async def server_info(self, ctx):
        guild = ctx.guild
        stats = await self.get_server_stats(guild)
        main_embed = await self.create_main_embed(ctx, stats)

        view = PaginatedView(ctx, self, stats)
        view.message = await ctx.send(embed=main_embed, view=view)


class PaginatedView(View):
    def __init__(self, ctx, cog: ServerInfo, stats):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.stats = stats
        self.cog = cog
        self.current_page = 0
        self.max_roles_pages = max((len(stats['roles']) - 1) // 10 + 1, 1)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "❌ Only the command author can use these buttons!", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="◀️")
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
        await self.update_view(interaction)

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="▶️")
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page < self.max_roles_pages:
            self.current_page += 1
        await self.update_view(interaction)

    async def update_view(self, interaction: discord.Interaction):
        if self.current_page == 0:
            embed = await self.cog.create_main_embed(self.ctx, self.stats)
        else:
            embed = await self.cog.create_roles_embed(self.ctx, self.stats, self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass


async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
