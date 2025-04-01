import json
import discord
from discord.ext import commands

def get_channel_id(guild_id, channel_name):
    with open('data/channel_ids.json', 'r') as f:
        data = json.load(f)
    guild_data = data.get(str(guild_id), {})
    return guild_data.get(channel_name)

class BanStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ban_processed = set()

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if user.id in self.ban_processed:
            return
        self.ban_processed.add(user.id)

        # Get the ban-status channel ID from the file
        ban_status_channel_id = get_channel_id(guild.id, 'ban_status_channel_id')
        if not ban_status_channel_id:
            print(f"ID kênh ban-status không tồn tại trong file channel_ids.json cho guild {guild.id}.")
            return

        # Get the ban-status channel
        ban_status_channel = guild.get_channel(ban_status_channel_id)
        if not ban_status_channel:
            print(f"Không tìm thấy kênh ban-status với ID {ban_status_channel_id} trong guild {guild.id}.")
            return

        # Get the reason for the ban and the user who performed the ban
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                reason = entry.reason if entry.reason else "Không có lý do cụ thể."
                banned_by = entry.user
                break
        else:
            reason = "Không có lý do cụ thể."
            banned_by = None

        # Create the embed message
        embed = discord.Embed(
            title="Thành viên bị cấm",
            description=f"{user.mention} đã bị cấm khỏi server.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        embed.add_field(name="Tên người dùng", value=user.name, inline=True)
        embed.add_field(name="ID người dùng", value=user.id, inline=True)

        if banned_by:
            embed.add_field(name="Bị cấm bởi", value=banned_by.mention, inline=False)

        embed.add_field(name="Lý do", value=reason, inline=False)

        # Add footer with bot icon
        embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)

        # Send the notification to the ban-status channel
        await ban_status_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BanStatus(bot))