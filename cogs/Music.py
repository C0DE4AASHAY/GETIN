import nextcord
from nextcord.ext import commands
import yt_dlp
from nextcord import FFmpegOpusAudio
from collections import deque
import urllib.parse


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.queues = {}
        self.now_playing = {}
        self.voice_channel_id = None  # Store the VC ID where bot will stay
        self.check_vc.start()  # Background loop start

        # yt-dlp settings optimized for better quality
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
                'preferredquality': '192',
            }],
        }

    def setup_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()

    @commands.command(name="play")
    async def play(self, ctx, *, query):
        """Play a song from YouTube."""
        if not ctx.author.voice:
            return await ctx.send("❌ You must be in a voice channel!")

        if not ctx.voice_client:
            await ctx.invoke(self.join)

        self.setup_queue(ctx.guild.id)

        # Check if input is a URL or search query
        if not urllib.parse.urlparse(query).scheme:
            query = f"ytsearch:{query}"

        async with ctx.typing():
            try:
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    if 'entries' in info:
                        url = info['entries'][0]['url']
                        title = info['entries'][0]['title']
                    else:
                        url = info['url']
                        title = info['title']

                    self.queues[ctx.guild.id].append({'url': url, 'title': title})
                    await ctx.send(f"✅ Added to queue: {title}")

                    if not ctx.voice_client.is_playing():
                        await self.play_next(ctx)
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)}")

    async def play_next(self, ctx):
        if not self.queues[ctx.guild.id]:
            await ctx.send("✅ Queue finished!")
            return

        if ctx.voice_client:
            song = self.queues[ctx.guild.id].popleft()
            self.now_playing[ctx.guild.id] = song

            # Optimized FFmpeg settings for better sound
            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn -b:a 192k -bufsize 64k'
            }

            def after_play(err):
                if err:
                    print(f"Player error: {err}")
                self.bot.loop.call_soon_threadsafe(self.bot.loop.create_task, self.play_next(ctx))

            ctx.voice_client.play(
                FFmpegOpusAudio(song['url'], **FFMPEG_OPTIONS),
                after=after_play
            )
            await ctx.send(f"🎵 Now playing: {song['title']}")

    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pause the current song."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Music paused!")
        else:
            await ctx.send("❌ Nothing is playing!")

    @commands.command(name="resume")
    async def resume(self, ctx):
        """Resume the paused song."""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed!")
        else:
            await ctx.send("❌ Music is not paused!")

    @commands.command(name="skip")
    async def skip(self, ctx):
        """Skip the current song."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped the current song")
        else:
            await ctx.send("❌ Nothing is playing!")

    @commands.command(name="queue")
    async def queue(self, ctx):
        """Show the current queue."""
        if not self.queues.get(ctx.guild.id):
            return await ctx.send("❌ Queue is empty!")

        queue_list = []
        if self.now_playing.get(ctx.guild.id):
            queue_list.append(f"Now Playing: {self.now_playing[ctx.guild.id]['title']}")
        
        for i, song in enumerate(self.queues[ctx.guild.id], 1):
            queue_list.append(f"{i}. {song['title']}")

        await ctx.send("\n".join(queue_list) if queue_list else "Queue is empty!")

    @commands.command(name="join")
    async def join(self, ctx):
        """Join the voice channel."""
        if not ctx.author.voice:
            return await ctx.send("❌ You are not connected to a voice channel.")
        

        channel = ctx.author.voice.channel

        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f"✅ Moved to {channel.name}")
        else:
            try:
                voice_client = await channel.connect()
                self.voice_clients[ctx.guild.id] = voice_client
                await ctx.send(f"✅ Joined {channel.name}")
            except Exception as e:
                await ctx.send(f"❌ Failed to join the voice channel: {e}")

    @commands.command(name="leave")
    async def leave(self, ctx):
        """Leave the voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            if ctx.guild.id in self.voice_clients:
                del self.voice_clients[ctx.guild.id]
            await ctx.send("👋 Left the voice channel")
        else:
            await ctx.send("❌ I'm not in a voice channel")

def setup(bot):
    bot.add_cog(Music(bot))
