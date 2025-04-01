import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from datetime import timedelta

class MuteUnmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Mute một thành viên trong khoảng thời gian nhất định")
    @has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, time: int, *, reason=None):
        try:
            duration = timedelta(minutes=time)  # Thời gian timeout
            await member.timeout_for(duration, reason=reason)
            embed = discord.Embed(
                title="Thành viên bị mute",
                description=f'Đã mute {member.mention} trong {time} phút vì lý do: {reason}',
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Lỗi",
                description=f'Không thể mute thành viên. Lỗi: {e}',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(help="Unmute một thành viên")
    @has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        try:
            await member.timeout(None)  # Hủy trạng thái timeout
            embed = discord.Embed(
                title="Thành viên được unmute",
                description=f'Đã unmute {member.mention}.',
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Lỗi",
                description=f'Không thể unmute thành viên. Lỗi: {e}',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MuteUnmute(bot))