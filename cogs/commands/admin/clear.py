import discord
from discord.ext import commands

def has_permissions_or_owner(**perms):
    async def predicate(ctx):
        if ctx.author.id == ctx.bot.owner_id:
            return True
        resolved = ctx.channel.permissions_for(ctx.author)
        return all(getattr(resolved, name, None) == value for name, value in perms.items())
    return commands.check(predicate)

class ClearCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Xóa tin nhắn hoặc các kênh và danh mục\nCú pháp: ?clear chat [số lượng] hoặc ?clear ctg [danh sách_id]")
    @has_permissions_or_owner(administrator=True)
    async def clear(self, ctx, action: str, *, identifiers: str):
        if action == "chat" and identifiers.isdigit():
            amount = int(identifiers)
            if amount > 0:
                deleted = await ctx.channel.purge(limit=amount)
                embed = discord.Embed(
                    title="Đã xóa tin nhắn",
                    description=f'Đã xóa {len(deleted)} tin nhắn.',
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed, delete_after=3)
            else:
                embed = discord.Embed(
                    title="Lỗi",
                    description="Số lượng tin nhắn phải lớn hơn 0.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
        elif action == "ctg":
            category_ids = identifiers.split(",")
            not_found_ids = []
            for identifier in category_ids:
                if identifier.strip().isdigit():
                    category_id = int(identifier.strip())
                    guild = ctx.guild
                    category = guild.get_channel(category_id)
                    if category and isinstance(category, discord.CategoryChannel):
                        for channel in category.channels:
                            await channel.delete()
                        await category.delete()
                    else:
                        not_found_ids.append(str(category_id))
                else:
                    not_found_ids.append(identifier.strip())
            
            if not_found_ids:
                embed = discord.Embed(
                    title="Lỗi",
                    description=f"Không tìm thấy danh mục với ID: {', '.join(not_found_ids)}.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Đã xóa danh mục",
                    description=f"Đã xóa toàn bộ các danh mục và kênh.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Lỗi cú pháp",
                description="Cú pháp không hợp lệ. Vui lòng sử dụng ?clear chat [số lượng] hoặc ?clear ctg [danh sách_id].",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(ClearCommandsCog(bot))