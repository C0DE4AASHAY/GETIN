import nextcord
from nextcord.ext import commands
import random
from database import get_balance, update_balance  # Import database functions

class MinesGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}  # Store ongoing games

    def generate_board(self, mine_count=5):
        board = [['⬜' for _ in range(5)] for _ in range(5)]
        mine_positions = random.sample(range(25), mine_count)

        for pos in mine_positions:
            row, col = divmod(pos, 5)
            board[row][col] = '💣'
        
        return board

    async def display_board(self, ctx, board, revealed):
        embed = nextcord.Embed(title="💎 Mines Game 💎", color=nextcord.Color.gold())
        description = ""

        for row in range(5):
            for col in range(5):
                if revealed[row][col]:
                    description += board[row][col] + " "
                else:
                    description += "🟦 "  # Unrevealed tile
            description += "\n"

        embed.description = description
        await ctx.send(embed=embed)

    @commands.command(name="m") # Mines Start
    async def start_mines(self, ctx, bet: int):
        """Start a Mines game with a bet."""
        if ctx.author.id in self.games:
            await ctx.send("❌ You are already playing a Mines game! Use `-ms` to stop it.")
            return

        # Check user balance
        user_balance = get_balance(ctx.author.id)
        if bet > user_balance:
            await ctx.send("❌ You don't have enough money to bet!")
            return

        # Deduct bet from balance
        update_balance(ctx.author.id, -bet)

        board = self.generate_board()
        revealed = [[False for _ in range(5)] for _ in range(5)]
        self.games[ctx.author.id] = {"board": board, "revealed": revealed, "bet": bet, "cashout": 0}

        await ctx.send(f"💎 *Mines Game Started!* Bet: {bet}\nUse `-r <row> <col>` to reveal a tile!")
        await self.display_board(ctx, board, revealed)

    @commands.command(name="r") # Mines Reveal
    async def reveal_tile(self, ctx, row: int, col: int):
        """Reveal a tile at (row, col)."""
        if ctx.author.id not in self.games:
            await ctx.send("❌ You are not playing a Mines game! Use `-m <bet>` to start one.")
            return

        game = self.games[ctx.author.id]
        board, revealed = game["board"], game["revealed"]

        if row < 0 or row > 4 or col < 0 or col > 4:
            await ctx.send("❌ Invalid tile position! Use numbers between 0-4.")
            return

        if revealed[row][col]:
            await ctx.send("⚠ You already revealed this tile!")
            return

        revealed[row][col] = True

        if board[row][col] == '💣':  # Player hits a mine
            await ctx.send(f"💥 *BOOM! You hit a mine and lost {game['bet']} coins!*")
            del self.games[ctx.author.id]
        else:
            game["cashout"] += game["bet"] * 0.2  # Increase cashout amount
            await ctx.send(f"✅ Safe! Your potential cashout: {game['cashout']}")
            await self.display_board(ctx, board, revealed)

    @commands.command(name="mc") # Mines Cashout
    async def cashout(self, ctx):
        """Cash out winnings before hitting a mine."""
        if ctx.author.id not in self.games:
            await ctx.send("❌ You are not playing a Mines game!")
            return

        game = self.games.pop(ctx.author.id)
        winnings = game["cashout"]

        # Add winnings to user balance
        update_balance(ctx.author.id, winnings)

        await ctx.send(f"💰 **You cashed out {winnings} coins!**")
    
    @commands.command(name="ms") # Mines Stop
    async def stop_mines(self, ctx):
        """Stop the game manually."""
        if ctx.author.id in self.games:
            del self.games[ctx.author.id]
            await ctx.send("❌ *Mines game stopped!*")
        else:
            await ctx.send("❌ You are not playing a Mines game!")

def setup(bot):
    bot.add_cog(MinesGame(bot))