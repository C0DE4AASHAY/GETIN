import discord
from discord.ext import commands
import json
import os

PREFIX_FILE = "Data/prefixes.json"

def load_prefixes():
    if not os.path.exists(PREFIX_FILE):
        return {}
    with open(PREFIX_FILE, "r") as f:
        return json.load(f)

def save_prefixes(data):
    with open(PREFIX_FILE, "w") as f:
        json.dump(data, f, indent=4)

class PrefixManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prefix")
    @commands.has_permissions(manage_guild=True)
    async def set_prefix(self, ctx, *, new_prefix: str = None):
        """Change or view server prefixes."""
        prefixes = load_prefixes()
        gid = str(ctx.guild.id)

        if new_prefix is None:
            # Show current prefixes in embed
            server_prefixes = prefixes.get(gid, [])
            embed = discord.Embed(
                title="🔧 Server Prefixes",
                description="Use -prefix <name>",
                color=discord.Color.blue()
            )
            embed.add_field(name="Default Prefix", value="`-`", inline=False)
            embed.add_field(
                name="New Prefix",
                value=", ".join(f"`{p}`" for p in server_prefixes) if server_prefixes else "None set.",
                inline=False
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        if len(new_prefix) > 5:
            await ctx.send("❌ Prefix too long! Keep it under 5 characters.")
            return

        if gid not in prefixes:
            prefixes[gid] = []

        if new_prefix in prefixes[gid]:
            await ctx.send(f"⚠️ The prefix `{new_prefix}` is already added.")
        else:
            prefixes[gid].append(new_prefix)
            save_prefixes(prefixes)
            await ctx.send(
                embed=discord.Embed(
                    title="✅ Prefix Updated",
                    description=f"New prefix `{new_prefix}` added successfully!",
                    color=discord.Color.green()
                )
            )

async def setup(bot):
    await bot.add_cog(PrefixManager(bot))
