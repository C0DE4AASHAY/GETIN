
    # game = nextcord.Streaming(name="F*ck your MoM",
                              # url="https://www.twitch.tv/yourstream")
    # await bot.change_presence(activity=game)


import nextcord
from nextcord.ext import commands, tasks
from datetime import datetime
import os
import asyncio
import nacl
import time
from collections.abc import Mapping
from nextcord.ext import tasks


# Initialize bot
intents = nextcord.Intents.all()
intents.message_content = True
intents.guilds = True
intents.invites = True
intents.voice_states = True 
intents.messages = True
bot = commands.Bot(command_prefix='-', intents=intents)
bot.remove_command('help')



@tasks.loop(seconds=5)
async def auto_reload():
    for cog in os.listdir("./cogs"):
        if cog.endswith(".py"):
            try:
                bot.unload_extension(f"cogs.{cog[:-3]}")
                bot.load_extension(f"cogs.{cog[:-3]}")
                print(f"🔄 Reloaded: {cog}")
            except Exception as e:
                print(f"⚠️ Error reloading {cog}: {e}")

@bot.event
async def on_ready():
    auto_reload.start()
    print(f"✅ Bot is online and auto-reloading cogs!")



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(f"Command not found: {ctx.message.content}")



@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

    # Start updating presence
    update_presence.start()



@tasks.loop(minutes=0.16)
async def update_presence():
    activity_listening = nextcord.Activity(type=nextcord.ActivityType.listening, name="-help")
    total_members = sum(guild.member_count or 0 for guild in bot.guilds)
    activity_watching = nextcord.Activity(type=nextcord.ActivityType.watching, name=f"{len(bot.guilds)} servers and {total_members} members")

    await bot.change_presence(activity=activity_listening)
    await asyncio.sleep(5)  # Wait for 5 seconds
    await bot.change_presence(activity=activity_watching)
    await asyncio.sleep(5)  # Wait for 5 seconds




@bot.command()
async def check(ctx):
    cmds = [cmd.name for cmd in bot.commands]
    await ctx.send(f"Available commands: {cmds}")




# Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        cog_name = filename[:-3]
        try:
            bot.load_extension(f'cogs.{cog_name}')
            print(f'Loaded extension: {cog_name}')
        except Exception as e:
            print(f'Error loading extension {cog_name}: {type(e).__name__} - {e}')



  
bot.run('BOT_TOKEN')

