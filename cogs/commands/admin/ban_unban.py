import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

class BanUnban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Cấm một thành viên khỏi máy chủ")
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="Đã Sút Thành Công",
                description=f'{member.mention} đã bị cấm khỏi máy chủ.',
                color=discord.Color.red()
            )
            embed.add_field(name="Lý do", value=reason if reason else "Không có lý do.")
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Lỗi",
                description=f'Không thể cấm thành viên.',
                color=discord.Color.red()
            )
            embed.add_field(name="Lỗi", value=str(e))
            await ctx.send(embed=embed)

    @commands.command(help="Unban một thành viên khỏi máy chủ")
    @has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        guild = ctx.guild
        user = await self.bot.fetch_user(user_id)
        try:
            await guild.unban(user)
            embed = discord.Embed(
                title="Đã Gỡ Cấm Thành Công",
                description=f'{user.mention} đã được gỡ cấm khỏi máy chủ.',
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Lỗi",
                description=f'Không thể gỡ cấm thành viên.',
                color=discord.Color.red()
            )
            embed.add_field(name="Lỗi", value=str(e))
            await ctx.send(embed=embed)

    @commands.command(help="Đá một thành viên khỏi máy chủ")
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="Đã Đá Thành Công",
                description=f'{member.mention} đã bị đá khỏi máy chủ.',
                color=discord.Color.orange()
            )
            embed.add_field(name="Lý do", value=reason if reason else "Không có lý do.")
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Lỗi",
                description=f'Không thể đá thành viên.',
                color=discord.Color.red()
            )
            embed.add_field(name="Lỗi", value=str(e))
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BanUnban(bot))