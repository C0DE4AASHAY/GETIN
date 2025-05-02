import discord
from discord import Embed, Color
from discord import app_commands, FFmpegPCMAudio
from discord.ext import commands
from discord.ui import View, Button
import yt_dlp
from datetime import timedelta
import asyncio
import urllib.parse
from collections import deque

class MusicPlayer:
    def __init__(self):
        self.queue = deque()
        self.loop = False
        self.now_playing = None

    def add_to_queue(self, song):
        self.queue.append(song)

    def next_song(self):
        if self.loop and self.now_playing:
            return self.now_playing
        self.now_playing = self.queue.popleft() if self.queue else None
        return self.now_playing


class PlaybackView(View):
    def __init__(self, ctx, bot, player: MusicPlayer):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.bot = bot
        self.player = player
        self.paused = False

    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.grey, custom_id="pause_resume")
    async def pause_resume_button(self, interaction: discord.Interaction, button: Button):
        vc = self.ctx.voice_client
        if vc:
            if not self.paused and vc.is_playing():
                vc.pause()
                button.label = "▶️ Resume"
                button.style = discord.ButtonStyle.green
                self.paused = True
                await interaction.response.edit_message(view=self)
            elif self.paused and vc.is_paused():
                vc.resume()
                button.label = "⏸️ Pause"
                button.style = discord.ButtonStyle.grey
                self.paused = False
                await interaction.response.edit_message(view=self)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.grey)
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client and self.ctx.voice_client.is_playing():
            self.ctx.voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped the song!", ephemeral=True)

    @discord.ui.button(label="⛔ Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client:
            await self.ctx.voice_client.disconnect()
            await interaction.response.send_message("⛔ Stopped and left the voice channel.", ephemeral=True)

    @discord.ui.button(label="🔁 Loop: OFF", style=discord.ButtonStyle.blurple)
    async def loop_button(self, interaction: discord.Interaction, button: Button):
        self.player.loop = not self.player.loop
        button.label = "🔁 Loop: ON" if self.player.loop else "🔁 Loop: OFF"
        await interaction.response.edit_message(view=self)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': False,
        }
        self.ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

    def get_player(self, guild_id):
        if guild_id not in self.players:
            self.players[guild_id] = MusicPlayer()
        return self.players[guild_id]

    @app_commands.command(name="play", description="Play a song from YouTube")
    async def play(self, interaction: discord.Interaction, song: str):
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        if not interaction.user.voice:
            embed = Embed(
                description="❌ Join a voice channel first to use this command.",
                color=Color.red()
            )
            return await interaction.followup.send(embed=embed)

        vc = interaction.guild.voice_client
        if not vc:
            vc = await interaction.user.voice.channel.connect()

        player = self.get_player(interaction.guild.id)

        if not urllib.parse.urlparse(song).scheme:
            song = f"ytsearch:{song}"

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(song, download=False)
                if 'entries' in info:
                    info = info['entries'][0]

                track = {
                    'title': info.get('title', 'Unknown'),
                    'url': info['url'],
                    'webpage_url': info.get('webpage_url'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'thumbnail': info.get('thumbnail'),
                    'requested_by': interaction.user.display_name
                }

                player.add_to_queue(track)
                await interaction.followup.send(f"✅ Added: {track['title']}")

                if not vc.is_playing():
                    await self.play_next(ctx)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    async def play_next(self, ctx):
        player = self.get_player(ctx.guild.id)
        song = player.next_song()
        if not song:
            await ctx.send("✅ Queue finished. Disconnecting...")
            await ctx.voice_client.disconnect()
            return

        def after_play(err):
            if err:
                print(f"Playback error: {err}")
            fut = self.play_next(ctx)
            asyncio.run_coroutine_threadsafe(fut, self.bot.loop)

        ctx.voice_client.play(FFmpegPCMAudio(song['url'], **self.ffmpeg_opts), after=after_play)

        duration = str(timedelta(seconds=song['duration'])) if song['duration'] else "?"
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"[{song['title']}]({song['webpage_url']})",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=song['thumbnail'])
        embed.add_field(name="🎤 Artist", value=song.get('uploader', 'Unknown'))
        embed.add_field(name="⏱️ Duration", value=duration)
        embed.add_field(name="🙋 Requested By", value=song.get('requested_by', 'Unknown'))
        await ctx.send(embed=embed, view=PlaybackView(ctx, self.bot, player))


async def setup(bot):
    await bot.add_cog(Music(bot))
