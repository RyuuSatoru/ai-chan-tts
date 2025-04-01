import os
import json
import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime

class ReportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blacklist = set()  # Đơn giản hóa blacklist bằng một set, lưu ID người dùng bị blacklist

    def load_invite_link(self, guild_id):
        file_path = "data/channel_ids.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                guild_data = data.get(str(guild_id))
                if guild_data:
                    return guild_data.get("invite_link")
        return None

    def add_to_blacklist(self, user_id):
        self.blacklist.add(user_id)
        # Bạn có thể lưu lại blacklist vào tệp nếu muốn lưu trữ lâu dài

    def remove_from_blacklist(self, user_id):
        self.blacklist.discard(user_id)

    @commands.command(name="report", aliases=["rp"], help="Gửi báo cáo lỗi hoặc vấn đề đến kênh chỉ định")
    async def report(self, ctx, *, message: str):
        report_channel_id = 1246079347090264147  # Thay thế bằng ID của kênh báo cáo
        report_channel = self.bot.get_channel(report_channel_id)

        if report_channel:
            guild = ctx.guild
            invite_link = self.load_invite_link(guild.id)
            current_time = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
            
            embed = discord.Embed(
                title=f"📢 Có phiếu báo cáo lỗi từ ID user: {ctx.author.id}",
                color=discord.Color.red()
            )
            embed.add_field(name="👤 Tên Người Gửi", value=ctx.author, inline=True)
            embed.add_field(name="🏷️ Tên Tag User", value=ctx.author.mention, inline=True)
            embed.add_field(name="🆔 ID Server", value=guild.id, inline=True)
            embed.add_field(name="🏷️ Tên Server", value=guild.name, inline=True)
            if invite_link:
                embed.add_field(name="🔗 Invite Link", value=f"[Click here]({invite_link})", inline=True)
            embed.add_field(name="", value="\u200b", inline=False)  # Khoảng cách giữa các trường
            embed.add_field(name="✉️ Nội Dung", value=message, inline=False)
            embed.add_field(name="", value="\u200b", inline=False)
            embed.set_footer(text=f"Được gửi bởi {ctx.author} | {current_time}", icon_url=ctx.author.avatar.url)

            view = View()

            # Nút phản hồi
            respond_button = Button(label="Phản hồi", style=discord.ButtonStyle.primary)
            async def respond_callback(interaction):
                if interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message(f"Đã phản hồi người dùng {ctx.author.mention}", ephemeral=True)
                else:
                    await interaction.response.send_message("Bạn không có quyền sử dụng nút này.", ephemeral=True)
            respond_button.callback = respond_callback
            view.add_item(respond_button)

            # Nút thêm vào blacklist
            blacklist_button = Button(label="Thêm vào blacklist", style=discord.ButtonStyle.danger)
            async def blacklist_callback(interaction):
                if interaction.user.guild_permissions.administrator:
                    self.add_to_blacklist(ctx.author.id)
                    await interaction.response.send_message(f"Đã thêm {ctx.author.mention} vào blacklist.", ephemeral=True)
                else:
                    await interaction.response.send_message("Bạn không có quyền sử dụng nút này.", ephemeral=True)
            blacklist_button.callback = blacklist_callback
            view.add_item(blacklist_button)

            await report_channel.send(embed=embed, view=view)
            await ctx.send("Báo cáo của bạn đã được gửi thành công, vui lòng đợi developer xử lý lỗi và phản hồi lại với bạn !!!")
        else:
            await ctx.send("Không tìm thấy kênh báo cáo. Vui lòng kiểm tra lại ID kênh.")

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(ReportCog(bot))