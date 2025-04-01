import os
import discord
import asyncio
from discord.ext import commands
from gtts import gTTS

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ffmpeg_executable = os.path.join(os.path.dirname(__file__),"Commands", 'ffmpeg', 'bin', 'ffmpeg.exe')  # Đường dẫn tuyệt đối đến ffmpeg.exe

    @commands.command(help="Dùng bot nói chuyện trong server voice\nCú pháp ?vs ngôn ngữ nội dung\n Ngôn ngữ hỗ trợ: vi, en, ja, ko, zh, fr, es, de, it")
    async def vs(self, ctx, lang: str, *, text: str):
        if ctx.author.voice is None:
            await ctx.send("Bạn phải ở trong kênh thoại để sử dụng lệnh này!")
            return
        
        voice_channel = ctx.author.voice.channel

        if ctx.voice_client and ctx.voice_client.channel != voice_channel:
            await ctx.send("Bạn phải ở cùng kênh thoại với bot để sử dụng lệnh này!")
            return

        # Chuyển văn bản thành giọng nói
        tts = gTTS(text=text, lang=lang)
        tts.save("tts.mp3")

        # Tham gia kênh thoại của người dùng nếu bot chưa tham gia
        if not ctx.voice_client:
            vc = await voice_channel.connect()
        else:
            vc = ctx.voice_client

        # Phát giọng nói
        try:
            vc.play(discord.FFmpegPCMAudio("tts.mp3", executable=self.ffmpeg_executable), after=lambda e: print('done', e))
        except discord.errors.ClientException as e:
            await ctx.send(f"Lỗi: {e}")
            return

        # Chờ đợi khi phát xong và sau đó xóa file
        while vc.is_playing():
            await asyncio.sleep(1)
        vc.stop()
        os.remove("tts.mp3")

        # Xóa tin nhắn sau 5 giây
        await asyncio.sleep(5)
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            print("Tin nhắn đã bị xóa hoặc không tìm thấy.")
        except discord.errors.Forbidden:
            print("Bot không có quyền xóa tin nhắn.")
        except discord.errors.HTTPException as e:
            print(f"Lỗi khi xóa tin nhắn: {e}")

async def setup(bot):
    await bot.add_cog(Voice(bot))