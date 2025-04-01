import json
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class ServerEventsCog(commands.Cog):
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
    async def on_guild_channel_create(self, channel):
        """Sự kiện khi kênh mới được tạo."""
        log_channel_id = self.get_channel_id(channel.guild.id, "server_update_channel_id")
        if not log_channel_id:
            print(f"ID kênh server-update không tồn tại trong file channel_ids.json cho guild {channel.guild.id}.")
            return

        log_channel = channel.guild.get_channel(int(log_channel_id))
        if not log_channel:
            print(f"Không tìm thấy kênh server-update với ID {log_channel_id}.")
            return

        entry = None
        async for log in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
            if log.target.id == channel.id:
                entry = log
                break

        embed = discord.Embed(
            title="Kênh Mới Được Tạo",
            description=f"Kênh {channel.mention} đã được tạo.",
            color=discord.Color.green()
        )
        if entry:
            embed.set_footer(text=f"Người tạo: {entry.user}", icon_url=entry.user.avatar.url)

        try:
            await log_channel.send(embed=embed)
            print(f"Sent embed to log channel {log_channel.name} (ID: {log_channel.id})")
        except discord.Forbidden as e:
            print(f"Không thể gửi tin nhắn vào kênh {log_channel.name} (ID: {log_channel.id}): {e}")
        except discord.HTTPException as e:
            print(f"Xảy ra lỗi khi gửi tin nhắn vào kênh {log_channel.name} (ID: {log_channel.id}): {e}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Sự kiện khi kênh bị xóa."""
        log_channel_id = self.get_channel_id(channel.guild.id, "server_update_channel_id")
        if not log_channel_id:
            print(f"ID kênh server-update không tồn tại trong file channel_ids.json cho guild {channel.guild.id}.")
            return

        log_channel = channel.guild.get_channel(int(log_channel_id))
        if not log_channel:
            print(f"Không tìm thấy kênh server-update với ID {log_channel_id}.")
            return

        entry = None
        async for log in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
            if log.target.id == channel.id:
                entry = log
                break

        embed = discord.Embed(
            title="Kênh Đã Bị Xóa",
            description=f"Kênh {channel.name} đã bị xóa.",
            color=discord.Color.red()
        )
        if entry:
            embed.set_footer(text=f"Người xóa: {entry.user}", icon_url=entry.user.avatar.url)

        try:
            await log_channel.send(embed=embed)
            print(f"Sent embed to log channel {log_channel.name} (ID: {log_channel.id})")
        except discord.Forbidden as e:
            print(f"Không thể gửi tin nhắn vào kênh {log_channel.name} (ID: {log_channel.id}): {e}")
        except discord.HTTPException as e:
            print(f"Xảy ra lỗi khi gửi tin nhắn vào kênh {log_channel.name} (ID: {log_channel.id}): {e}")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """Sự kiện khi kênh được cập nhật."""
        log_channel_id = self.get_channel_id(after.guild.id, "server_update_channel_id")
        if not log_channel_id:
            print(f"ID kênh server-update không tồn tại trong file channel_ids.json cho guild {after.guild.id}.")
            return

        log_channel = after.guild.get_channel(int(log_channel_id))
        if not log_channel:
            print(f"Không tìm thấy kênh server-update với ID {log_channel_id}.")
            return

        entry = None
        async for log in after.guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1):
            if log.target.id == after.id:
                entry = log
                break

        if before.name != after.name:
            embed = discord.Embed(
                title="Tên Kênh Đã Thay Đổi",
                description=f"Tên kênh đã được đổi từ {before.name} thành {after.mention}.",
                color=discord.Color.blue()
            )
            if entry:
                embed.set_footer(text=f"Người thay đổi: {entry.user}", icon_url=entry.user.avatar.url)

            try:
                await log_channel.send(embed=embed)
                print(f"Sent embed to log channel {log_channel.name} (ID: {log_channel.id})")
            except discord.Forbidden as e:
                print(f"Không thể gửi tin nhắn vào kênh {log_channel.name} (ID: {log_channel.id}): {e}")
            except discord.HTTPException as e:
                print(f"Xảy ra lỗi khi gửi tin nhắn vào kênh {log_channel.name} (ID: {log_channel.id}): {e}")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Sự kiện khi vai trò mới được tạo."""
        log_channel_id = self.get_channel_id(role.guild.id, "server_update_channel_id")
        if not log_channel_id:
            print(f"ID kênh server-update không tồn tại trong file channel_ids.json cho guild {role.guild.id}.")
            return

        log_channel = role.guild.get_channel(int(log_channel_id))
        if not log_channel:
            print(f"Không tìm thấy kênh server-update với ID {log_channel_id}.")
            return

        entry = None
        async for log in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
            if log.target.id == role.id:
                entry = log
                break

        embed = discord.Embed(
            title="Vai Trò Mới Được Tạo",
            description=f"Vai trò {role.mention} đã được tạo.",
            color=discord.Color.green()
        )
        if entry:
            embed.set_footer(text=f"Người tạo: {entry.user}", icon_url=entry.user.avatar.url)

        try:
            await log_channel.send(embed=embed)
            print(f"Sent embed to log channel {log_channel.name} (ID: {log_channel.id})")
        except discord.Forbidden as e:
            print(f"Không thể gửi tin nhắn vào kênh {log_channel.name} (ID: {log_channel.id}): {e}")
        except discord.HTTPException as e:
            print(f"Xảy ra lỗi khi gửi tin nhắn vào kênh {log_channel.name} (ID: {log_channel.id}): {e}")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Sự kiện khi vai trò bị xóa."""
        log_channel_id = self.get_channel_id(role.guild.id, "server_update_channel_id")
        if not log_channel_id:
            print(f"ID kênh server-update không tồn tại trong file channel_ids.json cho guild {role.guild.id}.")
            return

        log_channel = role.guild.get_channel(int(log_channel_id))
        if not log_channel:
            print(f"Không tìm thấy kênh server-update với ID {log_channel_id}.")
            return

        entry = None
        async for log in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
            if log.target.id == role.id:
                entry = log
                break

        embed = discord.Embed(
            title="Vai Trò Đã Bị Xóa",
            description=f"Vai trò {role.name} đã bị xóa.",
            color=discord.Color.red()
        )
        if entry:
            embed.set_footer(text=f"Người xóa: {entry.user}", icon_url=entry.user.avatar.url)

        try:
            await log_channel.send(embed=embed)
            print(f"Sent embed to log channel {log_channel.name} (ID: {log_channel.id})")
        except discord.Forbidden as e:
            print(f"Không thể gửi tin nhắn vào kênh {log_channel.name} (ID: {log_channel.id}): {e}")
        except discord.HTTPException as e:
            print(f"Xảy ra lỗi khi gửi tin nhắn vào kênh {log_channel.name} (ID: {log_channel.id}): {e}")

async def setup(bot):
    await bot.add_cog(ServerEventsCog(bot))