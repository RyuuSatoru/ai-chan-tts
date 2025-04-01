import discord
from discord.ext import commands

class GetAvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar", help="Lấy avatar từ lệnh người dùng cung cấp\nCú pháp: ?avatar (@taguser)")
    async def avatar(self, ctx, member: discord.Member):
        # Kiểm tra nếu người dùng có avatar dạng GIF
        if member.avatar.is_animated():
            avatar_url = member.avatar.replace(format="gif", size=1024).url
        else:
            avatar_url = member.avatar.replace(format="png", size=1024).url

        # Lấy URL avatar của user được tag với kích thước lớn nhất
        avatar_url_png = member.avatar.replace(format="png", size=1024).url
        avatar_url_jpg = member.avatar.replace(format="jpg", size=1024).url
        avatar_url_webp = member.avatar.replace(format="webp", size=1024).url

        # Tạo các link ẩn cho các định dạng ảnh avatar
        gif_link = f"[gif]({avatar_url})" if member.avatar.is_animated() else ""
        png_link = f"[png]({avatar_url_png})"
        jpg_link = f"[jpg]({avatar_url_jpg})"
        webp_link = f"[webp]({avatar_url_webp})"

        # Tạo embed cho avatar của user được tag
        embed = discord.Embed(title=f"{member.display_name}'s Avatar")
        embed.description = f"Tải ảnh theo dạng link:\n{gif_link} | {png_link} | {jpg_link} | {webp_link}".strip()
        embed.set_image(url=avatar_url)

        # Gửi embed
        await ctx.send(embed=embed)

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(GetAvatarCog(bot))