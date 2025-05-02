import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import string
from datetime import datetime

BACKUP_DIR = "backups"
INDEX_FILE = f"{BACKUP_DIR}/backup_index.json"
os.makedirs(BACKUP_DIR, exist_ok=True)
if not os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "w") as f:
        json.dump([], f)

def generate_backup_id(length=12):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def load_index():
    with open(INDEX_FILE, "r") as f:
        return json.load(f)

def save_index(index):
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=4)

class BackupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def backup_id_autocomplete(self, interaction: discord.Interaction, current: str):
        index = load_index()
        return [
            app_commands.Choice(
                name=f"{entry['guild_name']} | {entry['created_at']} ({entry['backup_id']})",
                value=entry["backup_id"]
            )
            for entry in index if current.lower() in entry["backup_id"].lower()
        ][:25]

    @app_commands.command(name="backup_create", description="Create a backup of this server.")
    async def backup_create(self, interaction: discord.Interaction):
        await interaction.response.send_message("📦 Creating backup...", ephemeral=True)

        guild = interaction.guild
        backup_id = generate_backup_id()
        backup = {
            "id": backup_id,
            "guild_name": guild.name,
            "roles": [],
            "channels": []
        }

        for role in guild.roles[::-1]:
            if role.name != "@everyone":
                backup["roles"].append({
                    "name": role.name,
                    "color": role.color.value,
                    "permissions": role.permissions.value,
                    "mentionable": role.mentionable,
                    "hoist": role.hoist
                })

        for channel in guild.channels:
            channel_data = {
                "name": channel.name,
                "type": channel.type.name,
                "category": channel.category.name if channel.category else None
            }
            backup["channels"].append(channel_data)

        filepath = f"{BACKUP_DIR}/{backup_id}.json"
        with open(filepath, "w", encoding='utf-8') as f:
            json.dump(backup, f, indent=4)

        created_at = datetime.utcnow().strftime("%d. %b %Y – %H:%M")
        index = load_index()
        index.append({
            "backup_id": backup_id,
            "guild_id": str(guild.id),
            "guild_name": guild.name,
            "created_at": created_at
        })
        save_index(index)

        embed = discord.Embed(
            title="✅ Backup Created",
            description=f"Successfully created backup with the ID: `{backup_id}`",
            color=0x00ff00
        )
        embed.add_field(name="Usage", value=f"```/backup load backup_id: {backup_id}\n/backup info backup_id: {backup_id}```", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="backup_load", description="Load a backup by its ID.")
    @app_commands.describe(backup_id="The backup ID to restore")
    async def backup_load(self, interaction: discord.Interaction, backup_id: str):
        await interaction.response.send_message("♻️ Restoring backup... Please wait.", ephemeral=True)

        guild = interaction.guild
        path = f"{BACKUP_DIR}/{backup_id}.json"

        if not os.path.exists(path):
            await interaction.followup.send("❌ Backup not found.", ephemeral=True)
            return

        for channel in guild.channels:
            try:
                await channel.delete()
            except discord.HTTPException:
                pass

        for role in guild.roles:
            if role.name != "@everyone":
                try:
                    await role.delete()
                except discord.HTTPException:
                    pass

        with open(path, "r", encoding='utf-8') as f:
            backup = json.load(f)

        created_roles = {}
        for role_data in backup["roles"]:
            new_role = await guild.create_role(
                name=role_data["name"],
                permissions=discord.Permissions(role_data["permissions"]),
                colour=discord.Colour(role_data["color"]),
                hoist=role_data["hoist"],
                mentionable=role_data["mentionable"]
            )
            created_roles[role_data["name"]] = new_role

        category_map = {}

        for channel_data in backup["channels"]:
            if channel_data["type"] == "category":
                category = await guild.create_category_channel(name=channel_data["name"])
                category_map[channel_data["name"]] = category

        for channel_data in backup["channels"]:
            if channel_data["type"] == "text":
                await guild.create_text_channel(
                    name=channel_data["name"],
                    category=category_map.get(channel_data["category"])
                )
            elif channel_data["type"] == "voice":
                await guild.create_voice_channel(
                    name=channel_data["name"],
                    category=category_map.get(channel_data["category"])
                )

        await interaction.followup.send("✅ Backup restored successfully!", ephemeral=True)

    @app_commands.command(name="backup_info", description="Show info about a backup.")
    @app_commands.describe(backup_id="The backup ID to inspect")
    async def backup_info(self, interaction: discord.Interaction, backup_id: str):
        path = f"{BACKUP_DIR}/{backup_id}.json"
        if not os.path.exists(path):
            await interaction.response.send_message("❌ Backup not found.", ephemeral=True)
            return

        with open(path, "r", encoding='utf-8') as f:
            backup = json.load(f)

        embed = discord.Embed(
            title=f"📄 Backup Info - {backup_id}",
            description=f"Server Name: `{backup['guild_name']}`",
            color=0x3498db
        )
        embed.add_field(name="Roles", value=str(len(backup["roles"])), inline=True)
        embed.add_field(name="Channels", value=str(len(backup["channels"])), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="backup_delete", description="Delete a backup by ID.")
    @app_commands.describe(backup_id="The backup ID to delete")
    async def backup_delete(self, interaction: discord.Interaction, backup_id: str):
        path = f"{BACKUP_DIR}/{backup_id}.json"
        if not os.path.exists(path):
            await interaction.response.send_message("❌ Backup not found.", ephemeral=True)
            return

        try:
            os.remove(path)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Failed to delete file: {e}", ephemeral=True)
            return

        index = load_index()
        index = [entry for entry in index if entry["backup_id"] != backup_id]
        save_index(index)

        await interaction.response.send_message(f"🗑️ Backup `{backup_id}` has been deleted.", ephemeral=True)

    # This is required to add autocomplete after cog is loaded
    def register_autocompletes(self):
        self.backup_load.autocomplete("backup_id")(self.backup_id_autocomplete)
        self.backup_info.autocomplete("backup_id")(self.backup_id_autocomplete)
        self.backup_delete.autocomplete("backup_id")(self.backup_id_autocomplete)

async def setup(bot: commands.Bot):
    cog = BackupCog(bot)
    cog.register_autocompletes()
    await bot.add_cog(cog)
