import discord
from discord.ext import commands
from discord.ui import View, Button

class ListEmojiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Kiểm tra danh sách emoji trên máy chủ")
    async def emojilist(self, ctx):
        guild = ctx.guild
        emojis = guild.emojis

        if not emojis:
            await ctx.send("Máy chủ này không có emoji nào.")
            return

        embeds = []
        embed = discord.Embed(title=f"Danh sách emoji của {guild.name}",
                              color=discord.Color.red())
        char_count = 0
        emoji_count = 0  # Đếm số emoji trên mỗi trang

        for i, emoji in enumerate(emojis, start=1):
            creator = await emoji.guild.fetch_member(
                emoji.user.id) if emoji.user else "Không có thông tin"
            emoji_info = (f"**Emoji** {str(emoji)}\n"
                          f"**Tên Emoji:** {emoji.name}\n"
                          f"**ID Emoji:** {emoji.id}\n"
                          f"**Người tạo:** {creator}\n"
                          f"**Hoạt ảnh:** {'Có' if emoji.animated else 'Không'}")

            # Kiểm tra nếu thêm emoji_info sẽ làm embed vượt quá kích thước cho phép hoặc quá 5 emoji
            if char_count + len(emoji_info) > 1024 or emoji_count >= 5:
                embed.set_footer(text=f"Trang {len(embeds) + 1}")
                embeds.append(embed)
                embed = discord.Embed(title=f"Danh sách emoji của {guild.name}", color=discord.Color.red())
                char_count = 0
                emoji_count = 0

            embed.add_field(name=f"Emoji {i}", value=emoji_info, inline=False)
            char_count += len(emoji_info)
            emoji_count += 1

        # Thêm embed cuối cùng
        embed.set_footer(text=f"Trang {len(embeds) + 1}")
        embeds.append(embed)

        # Tạo các nút chuyển trang
        class EmojiPaginator(View):
            def __init__(self, embeds):
                super().__init__()
                self.embeds = embeds
                self.current_page = 0

                # Khởi tạo nút điều hướng
                self.prev_button = Button(style=discord.ButtonStyle.primary, label="◀️ Trang Trước Đó", disabled=True)
                self.next_button = Button(style=discord.ButtonStyle.primary, label="Trang Kế Tiếp ▶️", disabled=(len(embeds) <= 1))
                self.prev_button.callback = self.prev_page
                self.next_button.callback = self.next_page
                self.add_item(self.prev_button)
                self.add_item(self.next_button)

            async def prev_page(self, interaction: discord.Interaction):
                self.current_page -= 1
                if self.current_page == 0:
                    self.prev_button.disabled = True
                self.next_button.disabled = False  # Bật nút "Sau" nếu không phải trang cuối
                embed = self.embeds[self.current_page]
                embed.set_footer(text=f"Trang {self.current_page + 1} / {len(self.embeds)}")
                await interaction.response.edit_message(embed=embed, view=self)

            async def next_page(self, interaction: discord.Interaction):
                self.current_page += 1
                if self.current_page == len(self.embeds) - 1:
                    self.next_button.disabled = True
                self.prev_button.disabled = False  # Bật nút "Trước" nếu không phải trang đầu
                embed = self.embeds[self.current_page]
                embed.set_footer(text=f"Trang {self.current_page + 1} / {len(self.embeds)}")
                await interaction.response.edit_message(embed=embed, view=self)

        # Gửi trang đầu tiên với các nút điều hướng và footer hiển thị số trang
        first_embed = embeds[0]
        first_embed.set_footer(text=f"Trang 1 / {len(embeds)}")
        await ctx.send(embed=first_embed, view=EmojiPaginator(embeds))

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(ListEmojiCog(bot))