import discord
from discord.ext import commands
from google import genai
from PIL import Image
import requests
from io import BytesIO
from collections import defaultdict
import json
import os

class ChatBotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = genai.Client(api_key="AIzaSyBU-OGXZU05dthQmyD7OEs8IUh3HM2JRuA")
        self.message_memory = defaultdict(list)
        self.kanji_data = self.load_json_file("data/Kanji.json")
        self.vocabulary_data = self.load_json_file("data/Vocabulary.json")

    def load_json_file(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            print(f"File {filepath} not found.")
            return []

    @commands.command(name="cmt", help="Trò chuyện với bot.\nSử dụng:\n!cmt ms <nội dung> -Giải đáp thắc mắc\n!cmt bt <hình ảnh> - Phân tích bài tập")
    async def cmt(self, ctx, *, message: str):
        # Recall previous messages and responses
        recalled_messages = await self.recall_messages(ctx)

        if message.lower().startswith("ms"):
            message_content = message[3:]
            if ctx.message.reference:
                # Get the replied message content
                replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                message_content = replied_message.content + " " + message_content

            # Include recalled messages in the prompt
            recall_context = "\n".join([f"User: {user_msg}\nBot: {bot_resp}" for user_msg, bot_resp in recalled_messages])
            prompt = recall_context + "\n" + message_content + " Trả lời với giọng văn vui vẻ, năng động, nữ tính, Ví dụ: Ai-chan nghĩ rằng, theo như Ai-chan được biết..."

            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt, 
            )
            bot_response = response.text[:2000]
            await ctx.send(bot_response)

            # Store the message and response
            self.message_memory[ctx.channel.id].append((message, bot_response))

        elif message.lower().startswith("bt"):
            await self.process_image(ctx)

    async def process_image(self, ctx):
        if not ctx.message.attachments:
            await ctx.send("Vui lòng tải lên một hình ảnh để xử lý.")
            return

        attachment = ctx.message.attachments[0]
        if not attachment.content_type.startswith("image/"):
            await ctx.send("Vui lòng tải lên một tệp hình ảnh hợp lệ.")
            return

        response = requests.get(attachment.url)
        img = Image.open(BytesIO(response.content))

        analysis_prompt = [img, "Bắt đầu hướng dẫn như: Chào bạn, hãy cùng Ai-chan giải bài tập này nhé!...Trả về cấu trúc: Từ vựng, ngữ pháp, kết quả, đáp án"]
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=analysis_prompt,
        )
        bot_response = response.text[:2000]
        await ctx.send(bot_response)

        # Store the message and response
        self.message_memory[ctx.channel.id].append((ctx.message.content, bot_response))

    async def recall_messages(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.message_memory:
            return self.message_memory[channel_id]
        else:
            return []

    @commands.command(name="recall", help="Recall messages and bot responses.\nSử dụng:\n!recall - Hiển thị tin nhắn và phản hồi đã lưu")
    async def recall(self, ctx):
        recalled_messages = await self.recall_messages(ctx)
        if recalled_messages:
            for user_message, bot_response in recalled_messages:
                await ctx.send(f"User: {user_message}\nBot: {bot_response}")
        else:
            await ctx.send("Không có tin nhắn hoặc phản hồi nào được lưu.")

    @commands.command(name="kanji", help="Tìm thông tin Kanji.\nSử dụng:\n!kanji <level> - Hiển thị Kanji của cấp độ đó")
    async def kanji(self, ctx, level: int):
        kanji_list = [k for k in self.kanji_data if k['level'] == level]
        if kanji_list:
            response = "\n\n".join([f"Từ số {index+1}:\nKý tự: {k['character']}\nCó nghĩa là: {k['meaning']}\nÂm ghép (on): {k['onyomi']}\nÂm đơn (kun): {k['kunyomi']}" for index, k in enumerate(kanji_list)])
        else:
            response = f"Không tìm thấy Kanji cho cấp độ {level}."

        file_path = f"kanji_level_{level}.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response)
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)

        self.message_memory[ctx.channel.id].append((f"kanji {level}", response))

    @commands.command(name="vocabulary", help="Tìm thông tin từ vựng.\nSử dụng:\n!vocabulary <level> - Hiển thị từ vựng của cấp độ đó")
    async def vocabulary(self, ctx, level: int):
        vocabulary_list = [v for v in self.vocabulary_data if v['level'] == level]
        if vocabulary_list:
            response = "\n\n".join([f"Từ số {index+1}:\nKý tự: {v['character']}\nĐọc là: {v['kana']}\nCó nghĩa là: {v['meaning']}" for index, v in enumerate(vocabulary_list)])
        else:
            response = f"Không tìm thấy từ vựng cho cấp độ {level}."

        file_path = f"vocabulary_level_{level}.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response)
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)

        self.message_memory[ctx.channel.id].append((f"vocabulary {level}", response))

async def setup(bot):
    await bot.add_cog(ChatBotCog(bot))