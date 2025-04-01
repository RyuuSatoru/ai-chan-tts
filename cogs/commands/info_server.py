import discord
from discord.ext import commands

class ServerInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="serverinfo", help="Hiển thị thông tin chi tiết về server và số lượng slot emoji còn trống")
    async def serverinfo(self, ctx, server_id: str = None):
        if server_id:
            guild = self.bot.get_guild(int(server_id))
            if not guild:
                await ctx.send(f'Không tìm thấy server với ID: {server_id}')
                return
        else:
            guild = ctx.guild

        owner = guild.owner
        owner_tag = f'<@{owner.id}>' if owner else 'Không xác định'
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        member_count = guild.member_count
        created_at = guild.created_at.strftime("%d/%m/%Y")
        preferred_locale = guild.preferred_locale

        # Kiểm tra số lượng slot emoji còn trống
        total_emoji_slots = guild.emoji_limit
        total_animated_emoji_slots = guild.emoji_limit  # Số slot cho emoji động và tĩnh là như nhau

        # Lấy danh sách tất cả emoji và phân loại
        static_emojis = [emoji for emoji in guild.emojis if not emoji.animated]
        animated_emojis = [emoji for emoji in guild.emojis if emoji.animated]

        # Tính toán số slot còn trống
        used_static_emoji_slots = len(static_emojis)
        available_static_emoji_slots = total_emoji_slots - used_static_emoji_slots
        used_animated_emoji_slots = len(animated_emojis)
        available_animated_emoji_slots = total_animated_emoji_slots - used_animated_emoji_slots

        embed = discord.Embed(title=f"Tên Server: {guild.name}", color=discord.Color.blue())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="", value="**📄 Thông tin Server**", inline=False)
        embed.add_field(name="👑 Chủ server", value=owner_tag, inline=True)
        embed.add_field(name="👥 Tổng số người dùng và bots", value=str(member_count), inline=True)
        embed.add_field(name="💬 Kênh văn bản", value=str(text_channels), inline=True)
        embed.add_field(name="🔊 Kênh thoại", value=str(voice_channels), inline=True)
        embed.add_field(name="🌐 Ngôn ngữ ưa thích", value=str(preferred_locale), inline=True)
        embed.add_field(name="📅 Ngày tạo", value=created_at, inline=True)

        embed.add_field(name="", value="**😀 Thông tin slot emoji**", inline=False)
        embed.add_field(name="😀 Số emoji hiện tại", value=f"{used_static_emoji_slots} slot", inline=True)
        embed.add_field(name="➕ Số slot emoji có thể thêm", value=f"{available_static_emoji_slots} slot", inline=True)
        embed.add_field(name="🔢 Số slot emoji tĩnh tối đa của server", value=f"{total_emoji_slots} slot", inline=True)
        embed.add_field(name="🌀 Số emoji động hiện tại", value=f"{used_animated_emoji_slots} slot", inline=True)
        embed.add_field(name="➕ Số slot emoji động có thể thêm", value=f"{available_animated_emoji_slots} slot", inline=True)
        embed.add_field(name="🔢 Số slot emoji động tối đa của server", value=f"{total_animated_emoji_slots} slot", inline=True)

        await ctx.send(embed=embed)

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(ServerInfoCog(bot))