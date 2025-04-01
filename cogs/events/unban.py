import json
import discord
from discord.ext import commands

class UnbanStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.unban_processed = set()

    def get_channel_id(self, guild_id, channel_name):
        with open('data/channel_ids.json', 'r') as f:
            data = json.load(f)
        guild_data = data.get(str(guild_id), {})
        return guild_data.get(channel_name)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if user.id in self.unban_processed:
            return
        self.unban_processed.add(user.id)

        # Get the ban-status channel ID from the file
        ban_status_channel_id = self.get_channel_id(guild.id, "ban_status_channel_id")
        if not ban_status_channel_id:
            print(f"ID kênh ban-status không tồn tại trong file channel_ids.json cho guild {guild.id}.")
            return

        # Get the ban-status channel
        ban_status_channel = guild.get_channel(ban_status_channel_id)
        if not ban_status_channel:
            print("Không tìm thấy kênh ban-status.")
            return

        # Get information about the user who performed the unban
        unbanned_by = None
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            if entry.target.id == user.id:
                unbanned_by = entry.user
                break

        # Create the embed message
        embed = discord.Embed(
            title="Thành viên được gỡ cấm",
            description=f"{user.mention} đã được gỡ cấm khỏi server.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        embed.add_field(name="Tên người dùng", value=user.name, inline=True)
        embed.add_field(name="ID người dùng", value=user.id, inline=True)

        if unbanned_by:
            embed.add_field(name="Gỡ cấm bởi", value=unbanned_by.mention, inline=False)

        # Add footer with bot icon
        embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)

        # Send the notification to the ban-status channel
        await ban_status_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UnbanStatus(bot))