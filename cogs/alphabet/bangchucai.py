import discord
from discord.ext import commands

class AlphabetImageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bcc", help="Hiển thị bảng chữ cái Hiragana hoặc Katakana\nCú pháp: !bcc hira hoặc !bcc kata")
    async def bcc(self, ctx, alphabet_type: str):
        if alphabet_type.lower() == "hira":
            image_url = "https://nhatngucantho.com/wp-content/uploads/2022/03/bang-chu-cai-tieng-nhat-hiragana-nhat-ngu-can-tho-2.jpg"  
            embed_title = "Bảng chữ cái Hiragana"
        elif alphabet_type.lower() == "kata":
            image_url = "https://nhatngucantho.com/wp-content/uploads/2022/03/bang-chu-cai-tieng-nhat-katakana-nhat-ngu-can-tho-2.jpg"  
            embed_title = "Bảng chữ cái Katakana"
        else:
            await ctx.send("Vui lòng nhập 'hira' hoặc 'kata' để chọn bảng chữ cái.")
            return

        embed = discord.Embed(title=embed_title)
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(AlphabetImageCog(bot))