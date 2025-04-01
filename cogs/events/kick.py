import json
import discord
from discord.ext import commands

class KickStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kick_processed = set()

    def get_channel_id(self, guild_id, channel_name):
        with open('data/channel_ids.json', 'r') as f:
            data = json.load(f)
        guild_data = data.get(str(guild_id), {})
        return guild_data.get(channel_name)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Ensure this code is only processing the kick event
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                if member.id in self.kick_processed:
                    return
                self.kick_processed.add(member.id)

                # Get the ban-status channel ID from the file
                ban_status_channel_id = self.get_channel_id(member.guild.id, "ban_status_channel_id")
                if not ban_status_channel_id:
                    print(f"ID kênh ban-status không tồn tại trong file channel_ids.json cho guild {member.guild.id}.")
                    return

                # Get the ban-status channel
                ban_status_channel = member.guild.get_channel(ban_status_channel_id)
                if not ban_status_channel:
                    print("Không tìm thấy kênh ban-status.")
                    return

                # Get information about the user who performed the kick
                kicked_by = entry.user
                reason = entry.reason if entry.reason else "Không có lý do cụ thể."

                # Create the embed message
                embed = discord.Embed(
                    title="Thành viên đã bị kick",
                    description=f"{member.mention} đã bị kick khỏi server.",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                embed.add_field(name="Tên người dùng", value=member.name, inline=True)
                embed.add_field(name="ID người dùng", value=member.id, inline=True)

                if kicked_by:
                    embed.add_field(name="Bị kick bởi", value=kicked_by.mention, inline=False)

                embed.add_field(name="Lý do", value=reason, inline=False)

                # Add footer with bot icon
                embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)

                # Send the notification to the ban-status channel
                await ban_status_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(KickStatus(bot))