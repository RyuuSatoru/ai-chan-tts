import discord
import time
from discord.ext import commands

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Đo độ trễ của bot và thời gian thực hiện lệnh")
    async def ping(self, ctx):
        start_time = time.time()
        message = await ctx.send("Đang đo độ trễ...")
        end_time = time.time()

        # Đo độ trễ giữa bot và máy chủ Discord
        bot_latency = self.bot.latency * 1000  # Chuyển đổi từ giây sang mili giây
        message_latency = (end_time - start_time) * 1000  # Chuyển đổi từ giây sang mili giây
        command_response_time = (end_time - start_time) * 1000  # Chuyển đổi từ giây sang mili giây

        embed = discord.Embed(title="Đo Độ Trễ", color=discord.Color.green())
        embed.add_field(name="Độ trễ của bot", value=f"📶 {bot_latency:.2f}ms ({bot_latency / 1000:.2f} seconds)", inline=False)
        embed.add_field(name="Thời gian thực hiện lệnh", value=f"📶 {message_latency:.2f}ms ({message_latency / 1000:.2f} seconds)", inline=False)
        
        # Thêm thời gian phản hồi lệnh vào footer của embed message
        embed.set_footer(text=f"Thời gian phản hồi lệnh cần {command_response_time:.2f}ms ({command_response_time / 1000:.2f} seconds)")

        await message.edit(content=None, embed=embed)

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(PingCog(bot))