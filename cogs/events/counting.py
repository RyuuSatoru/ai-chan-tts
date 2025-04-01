import json
import discord
from discord.ext import commands, tasks

def get_channel_id(guild_id, channel_name):
    with open('data/channel_ids.json', 'r') as f:
        data = json.load(f)
    guild_data = data.get(str(guild_id), {})
    return guild_data.get(channel_name)

class CountingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_counts.start()

    @tasks.loop(seconds=30)  # Cập nhật mỗi 30 giây
    async def update_counts(self):
        for guild in self.bot.guilds:
            member_count = len([member for member in guild.members if not member.bot])
            bot_count = len([member for member in guild.members if member.bot])
            
            # Lấy ID kênh member và bot cho máy chủ hiện tại
            member_channel_id = get_channel_id(guild.id, 'member_voice_channel_id')
            bot_channel_id = get_channel_id(guild.id, 'bots_voice_channel_id')

            if member_channel_id:
                member_channel = guild.get_channel(member_channel_id)
                if member_channel:
                    await member_channel.edit(name=f"👾 Thành Viên: {member_count}")

            if bot_channel_id:
                bot_channel = guild.get_channel(bot_channel_id)
                if bot_channel:
                    await bot_channel.edit(name=f"👾 Bots: {bot_count}")

    @update_counts.before_loop
    async def before_update_counts(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(CountingCog(bot))