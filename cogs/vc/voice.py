import discord
from discord.ext import commands
from google import genai
from google.genai import types
import asyncio
import wave
import pyaudio
from collections import defaultdict

class ChatBotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = genai.Client(api_key="GEMINI_API_KEY", http_options={'api_version': 'v1alpha'})
        self.model = "gemini-2.0-flash-exp"
        self.config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                )
            )
        )
        self.message_memory = defaultdict(list)
        self.output_device = self.get_device_index_by_name("Ai-chan-voice")

    @commands.command(name="voice", help="Trò chuyện với bot qua kênh thoại.\nSử dụng:\n!voice <kênh thoại>")
    async def voice(self, ctx, voice_channel: discord.VoiceChannel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(voice_channel)
        
        await voice_channel.connect()

        await self.process_audio(ctx)

    @commands.command(name="list_outputs", help="Liệt kê các đầu ra âm thanh có sẵn.")
    async def list_outputs(self, ctx):
        p = pyaudio.PyAudio()
        output_list = []
        for i in range(p.get_device_count()):
            output_list.append(p.get_device_info_by_index(i).get('name'))
        
        # Thêm đầu ra âm thanh "Ai-chan-voice"
        output_list.append("Ai-chan-voice")

        await ctx.send(f"Các đầu ra âm thanh có sẵn:\n" + "\n".join(output_list))

    async def process_audio(self, ctx):
        if self.output_device is None:
            await ctx.send("Không tìm thấy đầu ra âm thanh 'Ai-chan-voice'.")
            return

        async with self.client.aio.live.connect(model=self.model, config=self.config) as session:
            message = "Hello? Gemini are you there?"
            await session.send(input=message, end_of_turn=True)

            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=24000,
                            output=True,
                            output_device_index=self.output_device)

            async for idx, response in async_enumerate(session.receive()):
                if response.data is not None:
                    stream.write(response.data)

            stream.stop_stream()
            stream.close()
            p.terminate()

    def get_device_index_by_name(self, device_name):
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            if p.get_device_info_by_index(i).get('name') == device_name:
                return i
        # Giả sử rằng "Ai-chan-voice" là một thiết bị ảo và gán chỉ số không tồn tại nếu không tìm thấy
        if device_name == "Ai-chan-voice":
            return -1
        return None

    async def recall_messages(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.message_memory:
            return self.message_memory[channel_id]
        else:
            return []

async def setup(bot):
    await bot.add_cog(ChatBotCog(bot))