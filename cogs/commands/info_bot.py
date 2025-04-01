import discord
from discord.ext import commands
import platform
import psutil
from datetime import datetime
import cpuinfo

class BotInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()

    @commands.command(name="botinfo", help="Hiển thị thông tin bot")
    async def botinfo(self, ctx):
        # Lấy thông tin cơ bản của bot
        bot_user = self.bot.user
        bot_id = bot_user.id
        bot_tag = str(bot_user)
        bot_mention = bot_user.mention
        bot_created_at = bot_user.created_at.strftime("%H:%M:%S | %d/%m/%Y")
        
        # Thời gian bot đã được khởi chạy
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split('.')[0]  # Bỏ phần mili giây

        # Thông tin hệ thống
        cpu_count = psutil.cpu_count()
        cpu_info = cpuinfo.get_cpu_info()
        cpu_name = cpu_info['brand_raw']

        # Lấy thông tin CPU mà bot đang sử dụng
        process = psutil.Process()
        cpu_usage_percent = process.cpu_percent(interval=1)

        # Lấy thông tin RAM mà bot đang sử dụng
        ram_used_mb = process.memory_info().rss / (1024 ** 2)  # Đổi sang MB
        ram_used_gb = process.memory_info().rss / (1024 ** 3)  # Đổi sang GB
        ram_total = psutil.virtual_memory().total / (1024 ** 3)  # Đổi sang GB
        if ram_used_mb >= 1024:
            ram_info = f"{ram_used_gb:.2f} GB / {ram_total:.2f} GB"
        else:
            ram_info = f"{ram_used_mb:.2f} MB / {ram_total:.2f} GB"

        # Hệ điều hành
        os_info = platform.system() + " " + platform.release()
        architecture = platform.architecture()[0]
        os_info_with_arch = f"{os_info} ({architecture})"

        # Tổng số server và thành viên
        total_guilds = len(self.bot.guilds)
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        total_commands = len(self.bot.commands)

        # Tạo embed
        embed = discord.Embed(title="Thông tin Bot", color=0x00ff00)
        embed.add_field(name="🆔 ID Bot", value=bot_id, inline=True)
        embed.add_field(name="🏷️ Tag Bot", value=bot_tag, inline=True)
        embed.add_field(name="👤 Mention Bot", value=bot_mention, inline=True)
        embed.add_field(name="📅 Ngày tạo Bot", value=bot_created_at, inline=True)
        embed.add_field(name="⏱️ Thời gian hoạt động", value=uptime_str, inline=True)
        embed.add_field(name="⚙️ Tổng số lệnh", value=total_commands, inline=True)
        embed.add_field(name="💻 Số nhân CPU đang sử dụng", value=cpu_count, inline=True)
        embed.add_field(name="💻 % CPU đã sử dụng", value=f"{cpu_usage_percent:.2f}%", inline=True)
        embed.add_field(name="🖥️ Tên CPU", value=cpu_name, inline=True)
        embed.add_field(name="🗄️ RAM đã sử dụng", value=ram_info, inline=True)
        embed.add_field(name="🖥️ Hệ điều hành", value=os_info_with_arch, inline=True)
        embed.add_field(name="🌐 Tổng số server", value=total_guilds, inline=True)
        embed.add_field(name="👥 Tổng số thành viên", value=total_members, inline=True)

        # Lấy avatar của bot
        bot_avatar_url = bot_user.avatar.url if bot_user.avatar else None

        # Thêm footer với avatar bot và dòng "Code by Creative - thời gian"
        current_time = datetime.now().strftime("%H:%M:%S | %d/%m/%Y")
        if bot_avatar_url:
            embed.set_footer(text=f"Code by Creative - {current_time}", icon_url=bot_avatar_url)
        else:
            embed.set_footer(text=f"Code by Creative - {current_time}")

        # Gửi embed
        await ctx.send(embed=embed)

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(BotInfoCog(bot))