import json
import discord
from discord.ext import commands

class MessageEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_channel_id(self, guild_id, channel_name):
        with open('data/channel_ids.json', 'r') as f:
            data = json.load(f)
        guild_data = data.get(str(guild_id), {})
        return guild_data.get(channel_name)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Sự kiện khi tin nhắn bị xóa."""
        
        if message.author.bot:
            return

        # Lấy ID kênh message-update cho máy chủ hiện tại
        message_update_channel_id = self.get_channel_id(message.guild.id, 'message_update_channel_id')
        if not message_update_channel_id:
            print(f"ID kênh message-update không tồn tại trong file channel_ids.json cho guild {message.guild.id}.")
            return

        # Lấy kênh message-update
        message_update_channel = message.guild.get_channel(message_update_channel_id)
        if not message_update_channel:
            print("Không tìm thấy kênh message-update.")
            return

        # Tạo embed thông báo xóa tin nhắn
        embed = discord.Embed(
            title="Tin nhắn đã bị xóa",
            description=(
                f"**Người dùng:** {message.author.mention}\n"
                f"**Kênh:** {message.channel.mention}\n"
                f"**Nội dung tin nhắn:**\n```fix\n{message.content}\n```"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)
        await message_update_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Sự kiện khi tin nhắn được chỉnh sửa."""
        
        if before.author.bot:
            return

        # Lấy ID kênh message-update cho máy chủ hiện tại
        message_update_channel_id = self.get_channel_id(before.guild.id, 'message_update_channel_id')
        if not message_update_channel_id:
            print(f"ID kênh message-update không tồn tại trong file channel_ids.json cho guild {before.guild.id}.")
            return

        # Lấy kênh message-update
        message_update_channel = before.guild.get_channel(message_update_channel_id)
        if not message_update_channel:
            print("Không tìm thấy kênh message-update.")
            return

        # Tạo embed thông báo chỉnh sửa tin nhắn
        if before.content != after.content:
            embed = discord.Embed(
                title="Tin nhắn đã được chỉnh sửa",
                description=(
                    f"**Người dùng:** {before.author.mention}\n"
                    f"**Kênh:** {before.channel.mention}\n"
                    f"**Trước:**\n```fix\n{before.content}\n```\n"
                    f"**Sau:**\n```fix\n{after.content}\n```"
                ),
                color=discord.Color.orange()
            )
            embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)
            await message_update_channel.send(embed=embed)

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(MessageEventsCog(bot))