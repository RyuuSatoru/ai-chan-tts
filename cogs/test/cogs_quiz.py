import discord
import json
import random
from discord.ext import commands
from discord.utils import get

class QuizCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = self.load_questions()
        self.role_thresholds = self.load_role_thresholds()

    def load_questions(self):
        with open('data/quiz_questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_role_thresholds(self):
        with open('data/role_thresholds.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Sự kiện khi thành viên mới tham gia server."""
        await self.send_quiz(member)

    @commands.command(name='kt', help='Nhấn !kt op để làm bài kiểm tra và lấy vai trò tương ứng.')
    async def kt(self, ctx, *, arg):
        """Command to retake the quiz."""
        if arg.lower() == 'op':
            await self.send_quiz(ctx.author)

    async def send_quiz(self, member):
        """Gửi câu hỏi trắc nghiệm cho thành viên mới."""
        if not isinstance(member, discord.Member):
            return

        try:
            dm_channel = await member.create_dm()
            await dm_channel.send("Chào mừng đến với máy chủ! Hãy trả lời 15 câu hỏi trắc nghiệm tiếng Nhật để được phân loại vai trò.")

            score = 0
            for question in self.questions:
                answer = await self.ask_question(dm_channel, question)
                if answer == question['answer']:
                    score += 1
            
            role_name = self.get_role_based_on_score(score)
            role = get(member.guild.roles, name=role_name)
            if role:
                await member.add_roles(role)
                await dm_channel.send(f"Bạn đã đạt được vai trò: {role_name}")
            else:
                await dm_channel.send(f"Không tìm thấy vai trò tương ứng: {role_name}")
        
        except Exception as e:
            print(f"Không thể gửi câu hỏi trắc nghiệm cho {member.name}: {e}")

    async def ask_question(self, dm_channel, question):
        """Gửi một câu hỏi và chờ câu trả lời."""
        def check(m):
            return m.author == dm_channel.recipient and m.channel == dm_channel

        options = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(question['options'])])
        await dm_channel.send(f"{question['question']}\n{options}")

        try:
            answer = await self.bot.wait_for('message', check=check, timeout=30)
            return int(answer.content) - 1
        except:
            return -1

    def get_role_based_on_score(self, score):
        """Lấy tên vai trò dựa trên điểm số."""
        for role, threshold in self.role_thresholds.items():
            if threshold['min_score'] <= score <= threshold['max_score']:
                return threshold['role_name']
        return None

async def setup(bot):
    await bot.add_cog(QuizCog(bot))