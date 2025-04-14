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
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)
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

    ### AUTOCOMPLETE HANDLER ###
    async def backup_id_autocomplete(self, interaction: discord.Interaction, current: str):
        index = load_index()
        results = []
        for entry in index:
            label = f"{entry['guild_name']} | {entry['created_at']} ({entry['backup_id']})"
            if current.lower() in entry["backup_id"].lower():
                results.append(app_commands.Choice(name=label, value=entry["backup_id"]))
        return results[:25]  # Max 25 choices

    ### CREATE BACKUP ###
    @app_commands.command(name="backup_create", description="Create a backup of this server.")
    async def backup_create(self, interaction: discord.Interaction):
        guild = interaction.guild
        await interaction.response.send_message("📦 Creating backup...", ephemeral=True)

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
                "type": str(channel.type),
                "category": channel.category.name if channel.category else None
            }
            backup["channels"].append(channel_data)

        # Save the backup file
        filepath = f"{BACKUP_DIR}/{backup_id}.json"
        with open(filepath, "w", encoding='utf-8') as f:
            json.dump(backup, f, indent=4)

        # Add to index
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

    ### LOAD BACKUP ###
    @app_commands.command(name="backup_load", description="Load a backup by its ID.")
    @app_commands.describe(backup_id="The backup ID to restore")
    @app_commands.autocomplete(backup_id=backup_id_autocomplete)
    async def backup_load(self, interaction: discord.Interaction, backup_id: str):
        guild = interaction.guild
        path = f"{BACKUP_DIR}/{backup_id}.json"

        if not os.path.exists(path):
            await interaction.response.send_message("❌ Backup not found.", ephemeral=True)
            return

        await interaction.response.send_message("♻️ Restoring backup... Please wait.", ephemeral=True)

        for channel in guild.channels:
            try:
                await channel.delete()
            except:
                pass

        for role in guild.roles:
            if role.name != "@everyone":
                try:
                    await role.delete()
                except:
                    pass

        with open(path, "r", encoding='utf-8') as f:
            backup = json.load(f)

        for role_data in backup["roles"]:
            await guild.create_role(
                name=role_data["name"],
                permissions=discord.Permissions(role_data["permissions"]),
                colour=discord.Colour(role_data["color"]),
                hoist=role_data["hoist"],
                mentionable=role_data["mentionable"]
            )

        for channel_data in backup["channels"]:
            channel_type = discord.ChannelType.text if "text" in channel_data["type"] else discord.ChannelType.voice
            if channel_type == discord.ChannelType.text:
                await guild.create_text_channel(name=channel_data["name"])
            else:
                await guild.create_voice_channel(name=channel_data["name"])

        await interaction.followup.send("✅ Backup restored successfully!", ephemeral=True)

    ### BACKUP INFO ###
    @app_commands.command(name="backup_info", description="Show info about a backup.")
    @app_commands.describe(backup_id="The backup ID to inspect")
    @app_commands.autocomplete(backup_id=backup_id_autocomplete)
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

    ### DELETE BACKUP ###
    @app_commands.command(name="backup_delete", description="Delete a backup by ID.")
    @app_commands.describe(backup_id="The backup ID to delete")
    @app_commands.autocomplete(backup_id=backup_id_autocomplete)
    async def backup_delete(self, interaction: discord.Interaction, backup_id: str):
        path = f"{BACKUP_DIR}/{backup_id}.json"
        if not os.path.exists(path):
            await interaction.response.send_message("❌ Backup not found.", ephemeral=True)
            return

        try:
            os.remove(path)
        except:
            await interaction.response.send_message("⚠️ Failed to delete file.", ephemeral=True)
            return

        # Remove from index
        index = load_index()
        index = [entry for entry in index if entry["backup_id"] != backup_id]
        save_index(index)

        await interaction.response.send_message(f"🗑️ Backup `{backup_id}` has been deleted.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BackupCog(bot))
