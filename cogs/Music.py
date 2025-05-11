import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = self.parse_duration(data.get('duration'))
        self.thumbnail = data.get('thumbnail')
        self.requested_by = data.get('requested_by', 'Unknown')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, requester=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]
        
        data['requested_by'] = requester
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @staticmethod
    def parse_duration(duration):
        if not duration:
            return "N/A"
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes}:{seconds:02}"

class MusicControlPanel(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
        
        # Previous button
        prev_button = discord.ui.Button(label="⏮ Previous", style=discord.ButtonStyle.secondary)
        prev_button.callback = self.prev_callback
        self.add_item(prev_button)
        
        # Pause button
        pause_button = discord.ui.Button(label="⏯ Pause", style=discord.ButtonStyle.primary)
        pause_button.callback = self.pause_callback
        self.add_item(pause_button)
        
        # Skip button
        skip_button = discord.ui.Button(label="⏭ Skip", style=discord.ButtonStyle.primary)
        skip_button.callback = self.skip_callback
        self.add_item(skip_button)
        
        # Stop button
        stop_button = discord.ui.Button(label="⏹ Stop", style=discord.ButtonStyle.danger)
        stop_button.callback = self.stop_callback
        self.add_item(stop_button)
        
        # Loop button
        loop_button = discord.ui.Button(label="🔁 Loop", style=discord.ButtonStyle.success)
        loop_button.callback = self.loop_callback
        self.add_item(loop_button)
    
    async def prev_callback(self, interaction):
        await interaction.response.send_message("Previous functionality not implemented yet.", ephemeral=True)
    
    async def pause_callback(self, interaction):
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)
        
        if vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸ Paused the music.", ephemeral=True)
        else:
            vc.resume()
            await interaction.response.send_message("▶ Resumed the music.", ephemeral=True)
    
    async def skip_callback(self, interaction):
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)
        
        vc.stop()
        await interaction.response.send_message("⏭ Skipped the current song.", ephemeral=True)
    
    async def stop_callback(self, interaction):
        guild_id = interaction.guild.id
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)
        
        self.cog.queues[guild_id] = []
        vc.stop()
        await vc.disconnect()
        await interaction.response.send_message("⏹ Stopped the music.", ephemeral=True)
    
    async def loop_callback(self, interaction):
        guild_id = interaction.guild.id
        self.cog.loop[guild_id] = not self.cog.loop.get(guild_id, False)
        status = "enabled" if self.cog.loop[guild_id] else "disabled"
        await interaction.response.send_message(f"🔁 Loop {status}.", ephemeral=True)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.loop = {}
        self.current = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    @commands.hybrid_command(name='play', description='Plays a song')
    async def play(self, ctx, *, query):
        """Plays from a url (almost anything yt-dlp supports)"""
        
        if not ctx.author.voice:
            return await ctx.send("You are not connected to a voice channel.")
        
        vc = ctx.voice_client
        
        if not vc:
            vc = await ctx.author.voice.channel.connect()
        
        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(
                    query, 
                    loop=self.bot.loop, 
                    stream=True,
                    requester=ctx.author.display_name
                )
            except Exception as e:
                return await ctx.send(f'An error occurred: {e}')
            
            queue = self.get_queue(ctx.guild.id)
            queue.append(player)
            self.current[ctx.guild.id] = player
            
            if not vc.is_playing():
                await self.play_next(ctx)
            else:
                embed = self.create_embed(player, "Added to Queue")
                await ctx.send(embed=embed, view=MusicControlPanel(self))

    async def play_next(self, ctx):
        vc = ctx.voice_client
        queue = self.get_queue(ctx.guild.id)
        
        if not queue:
            return
        
        player = queue.pop(0)
        self.current[ctx.guild.id] = player
        
        vc.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
        
        embed = self.create_embed(player, "Now Playing")
        await ctx.send(embed=embed, view=MusicControlPanel(self))

    def create_embed(self, player, status):
        embed = discord.Embed(
            title=status,
            description=f"[{player.title}]({player.url})",
            color=discord.Color.blue()
        )
        embed.add_field(name="Duration", value=player.duration, inline=True)
        embed.add_field(name="Requested By", value=player.requested_by, inline=True)
        if player.thumbnail:
            embed.set_thumbnail(url=player.thumbnail)
        return embed

    @commands.hybrid_command(name='queue', description='Shows the current queue')
    async def show_queue(self, ctx):
        """Displays the current queue"""
        queue = self.get_queue(ctx.guild.id)
        
        if not queue:
            return await ctx.send("The queue is empty.")
        
        embed = discord.Embed(title="Queue", color=discord.Color.blue())
        
        for i, player in enumerate(queue, 1):
            embed.add_field(
                name=f"{i}. {player.title}",
                value=f"Duration: {player.duration} | Requested by: {player.requested_by}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='skip', description='Skips the current song')
    async def skip(self, ctx):
        """Skips the current song"""
        vc = ctx.voice_client
        
        if not vc or not vc.is_playing():
            return await ctx.send("No music is playing.")
        
        vc.stop()
        await ctx.send("⏭ Skipped the current song.")

    @commands.hybrid_command(name='stop', description='Stops the music and clears the queue')
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        vc = ctx.voice_client
        
        if not vc:
            return await ctx.send("Not connected to a voice channel.")
        
        self.queues[ctx.guild.id] = []
        vc.stop()
        await vc.disconnect()
        await ctx.send("⏹ Stopped the music.")

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

async def setup(bot):
    await bot.add_cog(Music(bot))