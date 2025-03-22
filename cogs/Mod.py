import nextcord
from nextcord.ext import commands
from datetime import datetime

class SecurityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mods')
    async def security(self, ctx):
        server_name = ctx.guild.name if ctx.guild else "Unknown Server"
        embed = nextcord.Embed(
            title='Security Dashboard',
            description=#f'Server name: **{server_name}**\n\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Kick user__**: `-kick @username`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Ban User__**: `-ban @username`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Unban User__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Mute User__**: `_______`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Unmute User__**: `______`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Warn__**: `_____`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Report__**: `____`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Invite__**: `___`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Add Role__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Remove Role__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Soft Ban__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Purge__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Avatar__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Deafen User__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Undeafen User__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Move User__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Slow Mode__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Voice Kick__**: `-unban user_id`\n'
                        '<a:A_arrow_arrow:1190713832860037272> **__Timeout User__**: `-to @username {time}`\n',
            color=0x00ff00
        )

        # Calculate the bot's uptime
        uptime = datetime.utcnow() - self.bot.start_time

        # Set the footer with the formatted uptime
        #embed.set_footer(text=f'Made by asklord • {str(uptime)}')

        await ctx.send(embed=embed)
#=====================================FOR BAN MEMBERS===================================
    @commands.command()
    async def ban(self, ctx, member: nextcord.Member):
        if ctx.message.author.guild_permissions.ban_members:
            await member.ban()
            await ctx.send(f"{member.name} has been banned.")
        else:
            await ctx.send("You don't have permission to use this command.")
            
#=====================================FOR KICK MEMBERS==================================
    
    @commands.command()
    async def kick(self, ctx, member: nextcord.Member):
        if ctx.message.author.guild_permissions.kick_members:
            await member.kick()
            await ctx.send(f"{member.name} has been kicked.")
        else:
            await ctx.send("You don't have permission to use this command.")

#=====================================FOR UNBAN MEMBERS==================================




def setup(bot):
    bot.add_cog(SecurityCog(bot))