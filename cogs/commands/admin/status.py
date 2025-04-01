import discord
from discord.ext import commands

def has_permissions_or_owner(**perms):
    async def predicate(ctx):
        if ctx.author.id == ctx.bot.owner_id:
            return True
        resolved = ctx.channel.permissions_for(ctx.author)
        return all(getattr(resolved, name, None) == value for name, value in perms.items())
    return commands.check(predicate)

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Thay đổi trạng thái của bot\nCú pháp: ?status <trạng thái> <tin nhắn>\nTrạng thái có sẵn là: playing, listening, watching, streaming")
    @has_permissions_or_owner(administrator=True)
    async def status(self, ctx, status_type: str, *, status_message: str):
        activity = None
        if status_type.lower() == "playing":
            activity = discord.Game(name=status_message)
        elif status_type.lower() == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=status_message)
        elif status_type.lower() == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=status_message)
        elif status_type.lower() == "streaming":
            activity = discord.Streaming(name=status_message, url="https://www.youtube.com/@creative1896")
        else:
            await ctx.send("Loại trạng thái không hợp lệ. Các loại trạng thái có thể đặt: playing, listening, watching, streaming")
            return
        await self.bot.change_presence(activity=activity)
        await ctx.send(f"Đã thay đổi trạng thái của bot thành: {status_type} {status_message}")

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(StatusCog(bot))