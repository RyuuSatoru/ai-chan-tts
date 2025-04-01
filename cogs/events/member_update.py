import json
import discord
from discord.ext import commands

class MemberUpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_channel_id(self, guild_id, channel_name):
        try:
            with open('data/channel_ids.json', 'r') as f:
                data = json.load(f)
            guild_data = data.get(str(guild_id), {})
            return guild_data.get(channel_name)
        except FileNotFoundError:
            print("File data/channel_ids.json không tồn tại.")
            return None

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Sự kiện khi thông tin thành viên thay đổi."""
        
        # Lấy ID kênh member-update cho máy chủ hiện tại
        member_update_channel_id = self.get_channel_id(before.guild.id, 'member_update_channel_id')
        if not member_update_channel_id:
            print(f"ID kênh member-update không tồn tại trong file channel_ids.json cho guild {before.guild.id}.")
            return

        # Lấy kênh member-update
        member_update_channel = before.guild.get_channel(int(member_update_channel_id))
        if not member_update_channel:
            print(f"Không tìm thấy kênh member-update với ID {member_update_channel_id}.")
            return

        # Kiểm tra thay đổi tên hiển thị
        if before.display_name != after.display_name:
            embed = discord.Embed(
                title="Người dùng đã cập nhật tên hiển thị",
                description=f"{before.mention} đã thay đổi tên",
                color=discord.Color.blue()
            )
            embed.add_field(name="Tên cũ", value=before.display_name, inline=True)
            embed.add_field(name="Tên mới", value=after.display_name, inline=True)
            embed.set_thumbnail(url=after.display_avatar.url)

            # Thêm footer với icon bot
            embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)

            try:
                await member_update_channel.send(embed=embed)
                print(f"Sent embed to member update channel {member_update_channel.name} (ID: {member_update_channel.id})")
            except discord.Forbidden as e:
                print(f"Không thể gửi tin nhắn vào kênh {member_update_channel.name} (ID: {member_update_channel.id}): {e}")
            except discord.HTTPException as e:
                print(f"Xảy ra lỗi khi gửi tin nhắn vào kênh {member_update_channel.name} (ID: {member_update_channel.id}): {e}")

        # Kiểm tra thay đổi vai trò
        elif before.roles != after.roles:
            embed = discord.Embed(
                title="Người dùng có cập nhật về vai trò mới trong Server",
                description=f"{before.mention} đã được cập nhật vai trò.",
                color=discord.Color.purple()
            )
            embed.add_field(name="Vai trò cũ", value=", ".join([role.mention for role in before.roles]), inline=True)
            embed.add_field(name="Vai trò mới", value=", ".join([role.mention for role in after.roles]), inline=True)
            embed.set_thumbnail(url=after.display_avatar.url)

            # Thêm footer với icon bot
            embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)

            try:
                await member_update_channel.send(embed=embed)
                print(f"Sent embed to member update channel {member_update_channel.name} (ID: {member_update_channel.id})")
            except discord.Forbidden as e:
                print(f"Không thể gửi tin nhắn vào kênh {member_update_channel.name} (ID: {member_update_channel.id}): {e}")
            except discord.HTTPException as e:
                print(f"Xảy ra lỗi khi gửi tin nhắn vào kênh {member_update_channel.name} (ID: {member_update_channel.id}): {e}")

        # Kiểm tra thay đổi avatar
        elif before.display_avatar.url != after.display_avatar.url:
            embed = discord.Embed(
                title="Người dùng đã cập nhật avatar",
                description=f"{before.mention} đã thay đổi avatar của họ.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Avatar cũ", value=f"[Link cũ]({before.display_avatar.url})", inline=True)
            embed.add_field(name="Avatar mới", value=f"[Link mới]({after.display_avatar.url})", inline=True)
            embed.set_thumbnail(url=after.display_avatar.url)

            # Thêm footer với icon bot
            embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)

            try:
                await member_update_channel.send(embed=embed)
                print(f"Sent embed to member update channel {member_update_channel.name} (ID: {member_update_channel.id})")
            except discord.Forbidden as e:
                print(f"Không thể gửi tin nhắn vào kênh {member_update_channel.name} (ID: {member_update_channel.id}): {e}")
            except discord.HTTPException as e:
                print(f"Xảy ra lỗi khi gửi tin nhắn vào kênh {member_update_channel.name} (ID: {member_update_channel.id}): {e}")

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(MemberUpdateCog(bot))