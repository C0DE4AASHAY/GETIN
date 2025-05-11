import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
import os
import asyncio
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Prefix data file
PREFIX_FILE = "Data/prefixes.json"

def load_prefixes():
    if not os.path.exists(PREFIX_FILE):
        return {}
    with open(PREFIX_FILE, "r") as f:
        return json.load(f)

def save_prefixes(prefixes):
    with open(PREFIX_FILE, "w") as f:
        json.dump(prefixes, f, indent=4)

def get_prefix(bot, message):
    if not message.guild:
        return "-"
    prefixes = load_prefixes()
    guild_id = str(message.guild.id)
    custom_prefixes = prefixes.get(guild_id, [])
    return commands.when_mentioned_or("-", *custom_prefixes)(bot, message)

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.presences = True
intents.members = True
intents.invites = True
intents.voice_states = True
intents.messages = True


# Bot instance
bot = commands.Bot(command_prefix=get_prefix, intents=intents, application_id=1069222986751676497)
bot.remove_command('help')

# ----------------- Presence Update -----------------
@tasks.loop(seconds=10)
async def update_presence():
    total_members = sum((g.member_count or 0) for g in bot.guilds)
    activity1 = discord.Activity(type=discord.ActivityType.listening, name="/help")
    activity2 = discord.Activity(
        type=discord.ActivityType.watching,
        name=f"{len(bot.guilds)} servers and {total_members} members"
    )
    await bot.change_presence(activity=activity1)
    await asyncio.sleep(5)
    await bot.change_presence(activity=activity2)

# ----------------- Bot Ready -----------------
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        logging.info("✅ Slash commands synced.")
    except Exception as e:
        logging.error(f"❌ Error syncing slash commands: {type(e).__name__} - {e}")

    if not update_presence.is_running():
        update_presence.start()

    logging.info(f"✅ {bot.user.name} is online and ready!")

# ----------------- Prefix Command Checker -----------------
@bot.command()
async def check(ctx):
    cmds = ', '.join([cmd.name for cmd in bot.commands])
    await ctx.send(f"✅ Available commands: {cmds}")

# ----------------- Prefix Command Error Handler -----------------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("⚠️ Unknown command.")
        logging.warning(f"⚠️ Command not found: {ctx.message.content}")
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="🚫 Permission Denied",
            description="You don’t have permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        logging.warning(f"⛔ {ctx.author} tried to use a command without permission.")
    else:
        logging.error(f"❌ Unexpected error: {type(error).__name__} - {error}")
        raise error

# ----------------- Slash Command Error Handler -----------------
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="🚫 Permission Denied",
            description="You don’t have permission to use this slash command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message("⚠️ Unknown slash command.", ephemeral=True)
    else:
        logging.error(f"❌ Slash Command Error: {type(error).__name__} - {error}")
        try:
            await interaction.response.send_message("⚠️ Something went wrong!", ephemeral=True)
        except discord.errors.InteractionResponded:
            pass

# ----------------- Load Extensions -----------------
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logging.info(f"✅ Loaded extension: {filename}")
            except Exception as e:
                logging.error(f"❌ Error loading {filename}: {type(e).__name__} - {e}")

# ----------------- Start Bot -----------------
async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            logging.error("❌ Bot token not found in environment variables!")
            return
        await bot.start(token)

# ----------------- Entrypoint -----------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped by user (Ctrl+C). Exiting cleanly...")
