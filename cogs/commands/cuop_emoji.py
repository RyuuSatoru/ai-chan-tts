import discord
import requests
from discord.ext import commands
from discord.ext.commands import has_any_role

def has_permissions_or_owner(**perms):
    async def predicate(ctx):
        if ctx.author.id == ctx.bot.owner_id:
            return True
        resolved = ctx.channel.permissions_for(ctx.author)
        return all(getattr(resolved, name, None) == value for name, value in perms.items())
    return commands.check(predicate)

class CuopEmojiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_emoji_by_id(self, bot, emoji_id):
        for guild in bot.guilds:
            for emoji in guild.emojis:
                if emoji.id == emoji_id:
                    return emoji
        return None

    @commands.command(help="Cướp emoji từ link hoặc emoji\nCú pháp: ?cuopemoji (tên_emoji) (link|:emoji:)")
    @has_permissions_or_owner(administrator=True)
    async def cuopemoji(self, ctx, name: str, source: str):
        try:
            if source.startswith('http://') or source.startswith('https://'):
                # Nếu source là URL
                response = requests.get(source)
                response.raise_for_status()  # Kiểm tra nếu URL không hợp lệ hoặc không truy cập được
                image_data = response.content
            elif source.isdigit():
                # Nếu source là ID emoji
                emoji_id = int(source)
                emoji = await self.get_emoji_by_id(self.bot, emoji_id)
                if emoji:
                    emoji_url = str(emoji.url)
                    response = requests.get(emoji_url)
                    response.raise_for_status()  # Kiểm tra nếu URL không hợp lệ hoặc không truy cập được
                    image_data = response.content
                else:
                    embed = discord.Embed(
                        title="Lỗi",
                        description="Không tìm thấy emoji này, vui lòng đảm bảo link của bạn là link chuẩn.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
                    return
            elif source.startswith('<') and source.endswith('>'):
                # Nếu source là emoji Nitro hoặc custom emoji
                emoji_id = int(source.split(':')[-1][:-1])  # Lấy ID từ emoji custom
                emoji = await self.get_emoji_by_id(self.bot, emoji_id)
                if emoji:
                    emoji_url = str(emoji.url)
                    response = requests.get(emoji_url)
                    response.raise_for_status()  # Kiểm tra nếu URL không hợp lệ hoặc không truy cập được
                    image_data = response.content
                else:
                    embed = discord.Embed(
                        title="Lỗi",
                        description="Không tìm thấy emoji này, vui lòng đảm bảo link của bạn là link chuẩn.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
                    return
            else:
                embed = discord.Embed(
                    title="Lỗi",
                    description="URL hoặc emoji không hợp lệ, vui lòng cung cấp một URL, emoji hợp lệ\nĐảm bảo bạn đã viết đúng Cú pháp ?cuopemoji tên_emoji <link|:emoji:>",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Tạo emoji mới từ dữ liệu hình ảnh
            new_emoji = await ctx.guild.create_custom_emoji(name=name, image=image_data)
            embed = discord.Embed(
                title="Emoji Log",
                description=f'\nĐã cướp thành công emoji {new_emoji}\n\nTên emoji: `{name}`',
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title="Lỗi",
                description="Đã xảy ra lỗi khi tải hình ảnh từ URL, vui lòng thử lại\nĐảm bảo bạn đã viết đúng Cú pháp ?cuopemoji tên_emoji <link|:emoji:>",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            print(e)
        except discord.HTTPException as e:
            embed = discord.Embed(
                title="Lỗi",
                description="Đã xảy ra lỗi khi tạo emoji trên máy chủ, vui lòng kiểm tra lại\nĐảm bảo bạn đã viết đúng Cú pháp ?cuopemoji tên_emoji <link|:emoji:>",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            print(e)

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(CuopEmojiCog(bot))