import discord
from discord.ext import commands
from google import genai
from google.genai import types
import asyncio
import numpy as np
import sounddevice as sd
from collections import defaultdict

class ChatBotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = genai.Client(api_key="AIzaSyBU-OGXZU05dthQmyD7OEs8IUh3HM2JRuA", http_options={'api_version': 'v1alpha'})
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
        self.output_device_index = self.get_device_index_by_name("CABLE Output (VB-Audio Virtual Cable)")
        self.output_device_channels = self.get_device_channels(self.output_device_index)

    @commands.command(name="voice", help="Trò chuyện với bot qua kênh thoại.\nSử dụng:\n!voice <kênh thoại>")
    async def voice(self, ctx, voice_channel: discord.VoiceChannel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(voice_channel)
        
        await voice_channel.connect()

        await self.process_audio(ctx)

    @commands.command(name="list_outputs", help="Liệt kê các đầu ra âm thanh có sẵn.")
    async def list_outputs(self, ctx):
        devices = sd.query_devices()
        output_list = [device['name'] for device in devices if device['max_output_channels'] > 0]

        await ctx.send(f"Các đầu ra âm thanh có sẵn:\n" + "\n".join(output_list))

    async def process_audio(self, ctx):
        if self.output_device_index is None or self.output_device_channels is None:
            await ctx.send("Không tìm thấy đầu ra âm thanh 'CABLE Output (VB-Audio Virtual Cable)' hoặc số lượng kênh không hợp lệ.")
            return

        async with self.client.aio.live.connect(model=self.model, config=self.config) as session:
            message = "Hello? Gemini are you there?"
            await session.send(input=message, end_of_turn=True)

            def audio_callback(outdata, frames, time, status):
                if status:
                    print(status)
                try:
                    data = next(self.audio_generator)
                    outdata[:] = data
                except StopIteration:
                    raise sd.CallbackStop

            self.audio_generator = self.generate_audio(session)

            with sd.OutputStream(device=self.output_device_index, channels=self.output_device_channels, callback=audio_callback, dtype='int16', samplerate=24000):
                await asyncio.sleep(10)  # Adjust the duration as needed

    def get_device_index_by_name(self, device_name):
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device_name in device['name']:
                return i
        return None

    def get_device_channels(self, device_index):
        if device_index is not None:
            device_info = sd.query_devices(device_index)
            return device_info['max_output_channels']
        return None

    async def generate_audio(self, session):
        async for idx, response in self.async_enumerate(session.receive()):
            if response.data is not None:
                yield np.frombuffer(response.data, dtype='int16')

    async def recall_messages(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.message_memory:
            return self.message_memory[channel_id]
        else:
            return []

    async def async_enumerate(self, async_iterable, start=0):
        index = start
        async for item in async_iterable:
            yield index, item
            index += 1

async def setup(bot):
    # Unload the cog if it's already loaded
    if 'ChatBotCog' in bot.cogs:
        await bot.remove_cog('ChatBotCog')
    await bot.add_cog(ChatBotCog(bot))