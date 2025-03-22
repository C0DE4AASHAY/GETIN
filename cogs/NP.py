# import nextcord
# from nextcord.ext import commands
# from nextcord.ui import View, Button

# class NP(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

# class NowPlayingView(View):
#     def __init__(self, player, ctx):
#         super().__init__()
#         self.player = player
#         self.ctx = ctx

#     @nextcord.ui.button(label="Previous", style=nextcord.ButtonStyle.secondary)
#     async def previous(self, button: Button, interaction: nextcord.Interaction):
#         await interaction.response.send_message("⏮️ Previous functionality coming soon!", ephemeral=True)

#     @nextcord.ui.button(label="Resume", style=nextcord.ButtonStyle.success)
#     async def resume(self, button: Button, interaction: nextcord.Interaction):
#         if self.ctx.voice_client and self.ctx.voice_client.is_paused():
#             self.ctx.voice_client.resume()
#             await interaction.response.send_message("▶️ Resumed!", ephemeral=True)

#     @nextcord.ui.button(label="Skip", style=nextcord.ButtonStyle.primary)
#     async def skip(self, button: Button, interaction: nextcord.Interaction):
#         if self.ctx.voice_client and self.ctx.voice_client.is_playing():
#             self.ctx.voice_client.stop()
#             await interaction.response.send_message("⏭️ Skipped!", ephemeral=True)

#     @nextcord.ui.button(label="Stop", style=nextcord.ButtonStyle.danger)
#     async def stop(self, button: Button, interaction: nextcord.Interaction):
#         if self.ctx.voice_client:
#             await self.ctx.voice_client.disconnect()
#             await interaction.response.send_message("🛑 Stopped & Left VC!", ephemeral=True)

#     @nextcord.ui.button(label="Enable Loop", style=nextcord.ButtonStyle.secondary)
#     async def loop(self, button: Button, interaction: nextcord.Interaction):
#         await interaction.response.send_message("🔄 Looping feature coming soon!", ephemeral=True)

# async def send_now_playing(ctx, song):
#     """Update Now Playing Embed"""
#     embed = nextcord.Embed(title="🎵 Now Playing", color=0xFF0000)
#     embed.add_field(name="Track", value=f"[{song['title']}]({song['url']})", inline=False)
#     embed.add_field(name="Artist", value=song.get('artist', 'Unknown'), inline=True)
#     embed.add_field(name="Duration", value=song.get('duration', 'Unknown'), inline=True)
#     embed.add_field(name="Requested By", value=ctx.author.mention, inline=True)
#     embed.set_thumbnail(url=song.get('thumbnail', "https://i.imgur.com/5WydxBP.png"))

#     view = NowPlayingView(None, ctx)
#     await ctx.send(embed=embed, view=view)

# def setup(bot):
#     bot.add_cog(NP(bot))