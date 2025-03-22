import nextcord
from nextcord.ext import commands
import datetime
import asyncio


class SpamProtectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_message_count = {}
        self.spam_protection_enabled = True  # Default to True
        self.spam_timeout = set()  # Use a set to track users under timeout
        self.timeout_role_name = "Timeout"  # Adjust the role name as needed

    async def check_spam(self, message):
        if not self.spam_protection_enabled:
            return

        user_id = message.author.id
        current_time = datetime.datetime.now()

        # Check if the user is in the dictionary
        if user_id in self.user_message_count:
            # Check if the time difference is within the threshold (e.g., 5 seconds)
            time_difference = current_time - self.user_message_count[user_id]['last_message_time']
            if time_difference.total_seconds() < 5:
                # Increment the message count for the user
                self.user_message_count[user_id]['message_count'] += 1
                # Check if the message count is above the threshold (e.g., 5 messages)
                if self.user_message_count[user_id]['message_count'] > 5 and user_id not in self.spam_timeout:
                    # Check if the user has admin permissions
                    if message.author.guild_permissions.administrator:
                        embed = nextcord.Embed(
                            title="Spam Protection",
                            description=f"{message.author.mention}, you're sending messages too quickly, but as an admin, you're exempt!",
                            color=0xFFD700  # Gold color
                        )
                        await message.channel.send(embed=embed)
                    else:
                        # Take action: mute or warn the user, etc.
                        embed = nextcord.Embed(
                            title="Spam Protection",
                            description=f"{message.author.mention}, you're sending messages too quickly! You are now under timeout...",
                            color=0xFF4500  # Red-Orange color
                        )
                        await message.channel.send(embed=embed)
                        await self.timeout_user(message.author)
            else:
                # Reset message count if the time threshold is exceeded
                self.user_message_count[user_id] = {'last_message_time': current_time, 'message_count': 1}
        else:
            # Add user to the dictionary if not present
            self.user_message_count[user_id] = {'last_message_time': current_time, 'message_count': 1}

    async def timeout_user(self, user):
        timeout_duration = 120  # Timeout duration in seconds (adjust as needed)
        self.spam_timeout.add(user.id)

        # Add timeout role to the user
        timeout_role = nextcord.utils.get(user.guild.roles, name=self.timeout_role_name)
        if timeout_role:
            await user.add_roles(timeout_role)

        await asyncio.sleep(timeout_duration)

        # Remove timeout role after timeout duration
        if timeout_role:
            await user.remove_roles(timeout_role)

        self.spam_timeout.remove(user.id)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return

        # Check for spam
        await self.check_spam(message)

    @commands.command(name='es')
    @commands.has_permissions(administrator=True)
    async def espam(self, ctx):
        self.spam_protection_enabled = True
        embed = nextcord.Embed(
            title="",
            description="**Spam protection has been enabled.**",
            color=0x00FF00  # Green color
        )
        await ctx.send(embed=embed)

    @commands.command(name='ds')
    @commands.has_permissions(administrator=True)
    async def dspam(self, ctx):
        self.spam_protection_enabled = False
        embed = nextcord.Embed(
            title="",
            description="**Spam protection has been disabled.**",
            color=0xFF0000  # Red color
        )
        await ctx.send(embed=embed)

    @commands.command(name='ss')
    async def spam_status(self, ctx):
        status = "enabled" if self.spam_protection_enabled else "disabled"
        embed = nextcord.Embed(
            title="",
            description=f"**Spam protection is currently {status}.**",
            color=0xFFFF00  # Yellow color
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(SpamProtectionCog(bot))
