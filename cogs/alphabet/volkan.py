import json
import random
import discord
import asyncio
from discord.ext import commands

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lv', help="Sử dụng: !lv kt - Bắt đầu bài kiểm tra kiến thức")
    async def level_up(self, ctx, subcommand=None):
        if subcommand == 'kt':
            await self.start_quiz(ctx)

    async def start_quiz(self, ctx):
        user_id = str(ctx.author.id)
        level_data = self.load_level_data()
        
        if user_id not in level_data['users']:
            level_data['users'][user_id] = 1

        level = level_data['users'][user_id]

        kanji_questions = self.load_questions('data/Kanji.json', level)
        vocab_questions = self.load_questions('data/Vocabulary.json', level)

        questions = random.sample(kanji_questions, 10) + random.sample(vocab_questions, 10)
        random.shuffle(questions)

        correct_answers = 0
        question_number = 0
        quiz_message = None
        user_answers = [None] * len(questions)
        confirmed_answers = [False] * len(questions)

        async def show_question(question_number, quiz_message, confirmed=False):
            question = questions[question_number]
            possible_answers = self.get_possible_answers(question, kanji_questions, vocab_questions)
            correct_answer = question['meaning']
            options = self.shuffle_options(correct_answer, possible_answers)

            embed = discord.Embed(title=f"Question {question_number + 1}: {question['character']}", description="Chữ này có nghĩa là gì?")
            embed.add_field(name="", value=f"A. {options[0]}", inline=False)
            embed.add_field(name="", value=f"B. {options[1]}", inline=False)
            embed.add_field(name="", value=f"C. {options[2]}", inline=False)
            embed.add_field(name="", value=f"D. {options[3]}", inline=False)

            view = discord.ui.View()
            if not confirmed:
                view.add_item(discord.ui.Button(label="A", style=discord.ButtonStyle.primary, custom_id="A"))
                view.add_item(discord.ui.Button(label="B", style=discord.ButtonStyle.primary, custom_id="B"))
                view.add_item(discord.ui.Button(label="C", style=discord.ButtonStyle.primary, custom_id="C"))
                view.add_item(discord.ui.Button(label="D", style=discord.ButtonStyle.primary, custom_id="D"))
            if question_number > 0:
                view.add_item(discord.ui.Button(label="Previous", style=discord.ButtonStyle.secondary, custom_id="previous"))
            if question_number < len(questions) - 1:
                view.add_item(discord.ui.Button(label="Next", style=discord.ButtonStyle.secondary, custom_id="next"))
            if question_number == len(questions) - 1:
                view.add_item(discord.ui.Button(label="Nộp bài", style=discord.ButtonStyle.success, custom_id="submit"))

            if quiz_message is None:
                quiz_message = await ctx.send(embed=embed, view=view)
            else:
                await quiz_message.edit(embed=embed, view=view)

            return quiz_message, correct_answer, options, embed, view

        quiz_message, correct_answer, options, embed, view = await show_question(question_number, quiz_message)

        def check(interaction):
            return interaction.user == ctx.author and interaction.message.id == quiz_message.id

        while True:
            try:
                interaction = await self.bot.wait_for('interaction', timeout=30.0, check=check)
                custom_id = interaction.data['custom_id']
                if custom_id in ['A', 'B', 'C', 'D'] and not confirmed_answers[question_number]:
                    user_answers[question_number] = custom_id
                    try:
                        await interaction.response.defer()
                    except discord.errors.NotFound:
                        await ctx.send('Không tìm thấy tương tác. Vui lòng thử lại.', delete_after=5)
                        break
                elif custom_id == "previous" and question_number > 0:
                    question_number -= 1
                    confirmed = confirmed_answers[question_number]
                    if confirmed:
                        embed = await self.update_embed_with_result(embed, options, correct_answer, user_answers[question_number])
                    try:
                        await interaction.response.defer()
                    except discord.errors.NotFound:
                        await ctx.send('Không tìm thấy tương tác. Vui lòng thử lại.', delete_after=5)
                        break
                    quiz_message, correct_answer, options, embed, view = await show_question(question_number, quiz_message, confirmed)
                elif custom_id == "next" and question_number < len(questions) - 1:
                    if user_answers[question_number] is not None:
                        confirmed_answers[question_number] = True
                        if (user_answers[question_number] == 'A' and options[0] == correct_answer) or \
                           (user_answers[question_number] == 'B' and options[1] == correct_answer) or \
                           (user_answers[question_number] == 'C' and options[2] == correct_answer) or \
                           (user_answers[question_number] == 'D' and options[3] == correct_answer):
                            correct_answers += 1
                            embed.set_field_at(0, name="", value=f"A. {options[0]}" + (" ✅" if user_answers[question_number] == "A" else ""))
                            embed.set_field_at(1, name="", value=f"B. {options[1]}" + (" ✅" if user_answers[question_number] == "B" else ""))
                            embed.set_field_at(2, name="", value=f"C. {options[2]}" + (" ✅" if user_answers[question_number] == "C" else ""))
                            embed.set_field_at(3, name="", value=f"D. {options[3]}" + (" ✅" if user_answers[question_number] == "D" else ""))
                        else:
                            correct_option = 'A' if options[0] == correct_answer else \
                                             'B' if options[1] == correct_answer else \
                                             'C' if options[2] == correct_answer else 'D'
                            embed.set_field_at(0, name="", value=f"A. {options[0]}" + (" ❌" if user_answers[question_number] == "A" else ""))
                            embed.set_field_at(1, name="", value=f"B. {options[1]}" + (" ❌" if user_answers[question_number] == "B" else ""))
                            embed.set_field_at(2, name="", value=f"C. {options[2]}" + (" ❌" if user_answers[question_number] == "C" else ""))
                            embed.set_field_at(3, name="", value=f"D. {options[3]}" + (" ❌" if user_answers[question_number] == "D" else ""))
                            embed.set_field_at(["A", "B", "C", "D"].index(correct_option), name=correct_option, value=f"{correct_option}. {options[["A", "B", "C", "D"].index(correct_option)]} ✅")
                        await quiz_message.edit(embed=embed, view=view)
                        await asyncio.sleep(2)  # Thêm khoảng thời gian trễ trước khi chuyển sang câu hỏi tiếp theo
                        question_number += 1
                        confirmed = confirmed_answers[question_number]
                        try:
                            await interaction.response.defer()
                        except discord.errors.NotFound:
                            await ctx.send('Không tìm thấy tương tác. Vui lòng thử lại.', delete_after=5)
                            break
                        quiz_message, correct_answer, options, embed, view = await show_question(question_number, quiz_message, confirmed)
                    else:
                        await ctx.send('Làm ơn chọn kết quả.', delete_after=5)
                elif custom_id == "submit":
                    break
            except asyncio.TimeoutError:
                await ctx.send('Bạn đã rời bài quá lâu!', delete_after=5)
                break

        embed = discord.Embed(title="Hoàn thành bài kiểm tra", description=f"Bạn đã trả lời đúng {correct_answers} trên {len(questions)} câu hỏi.")
        await quiz_message.edit(embed=embed, view=None)

        if correct_answers >= 18:
            level_data['users'][user_id] += 1
            await ctx.send(f"Chúc mừng! Bạn đã lên cấp {level_data['users'][user_id]}")
            await self.assign_role(ctx, ctx.author, level_data['users'][user_id])
        else:
            await ctx.send("Chưa vượt qua, nhấn !lv kt để thử lại!")

        self.save_level_data(level_data)

    async def assign_role(self, ctx, member, level):
        roles = {
            'N5': discord.utils.get(ctx.guild.roles, name='N5'),
            'N4': discord.utils.get(ctx.guild.roles, name='N4'),
            'N3': discord.utils.get(ctx.guild.roles, name='N3'),
            'N2': discord.utils.get(ctx.guild.roles, name='N2'),
            'N1': discord.utils.get(ctx.guild.roles, name='N1')
        }

        if level <= 10:
            role = roles['N5']
        elif 11 <= level <=20:
            role = roles['N4']
        elif 21 <= level <= 30:
            role = roles['N3']
        elif 31 <= level <= 40:
            role = roles['N2']        
        else:
            role = roles['N1']

        # Remove other level roles
        for r in roles.values():
            if r in member.roles:
                await member.remove_roles(r)

        # Assign the new role
        await member.add_roles(role)
        await ctx.send(f"{member.mention} đã được phân vai trò {role.name}.")

    async def update_embed_with_result(self, embed, options, correct_answer, user_answer):
        if user_answer is not None:
            if (user_answer == 'A' and options[0] == correct_answer) or \
               (user_answer == 'B' and options[1] == correct_answer) or \
               (user_answer == 'C' and options[2] == correct_answer) or \
               (user_answer == 'D' and options[3] == correct_answer):
                embed.set_field_at(0, name="", value=f"A. {options[0]}" + (" ✅" if user_answer == "A" else ""))
                embed.set_field_at(1, name="", value=f"B. {options[1]}" + (" ✅" if user_answer == "B" else ""))
                embed.set_field_at(2, name="", value=f"C. {options[2]}" + (" ✅" if user_answer == "C" else ""))
                embed.set_field_at(3, name="", value=f"D. {options[3]}" + (" ✅" if user_answer == "D" else ""))
            else:
                correct_option = 'A' if options[0] == correct_answer else \
                                 'B' if options[1] == correct_answer else \
                                 'C' if options[2] == correct_answer else 'D'
                embed.set_field_at(0, name="", value=f"A. {options[0]}" + (" ❌" if user_answer == "A" else ""))
                embed.set_field_at(1, name="", value=f"B. {options[1]}" + (" ❌" if user_answer == "B" else ""))
                embed.set_field_at(2, name="", value=f"C. {options[2]}" + (" ❌" if user_answer == "C" else ""))
                embed.set_field_at(3, name="", value=f"D. {options[3]}" + (" ❌" if user_answer == "D" else ""))
                embed.set_field_at(["A", "B", "C", "D"].index(correct_option), name=correct_option, value=f"{correct_option}. {options[["A", "B", "C", "D"].index(correct_option)]} ✅")
        return embed

    def load_level_data(self):
        with open('data/levels.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_level_data(self, data):
        with open('data/levels.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_questions(self, filepath, level):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [q for q in data if q['level'] == level]

    def get_possible_answers(self, correct_question, kanji_questions, vocab_questions):
        all_meanings = [q['meaning'] for q in kanji_questions + vocab_questions if q != correct_question]
        return random.sample(all_meanings, 3)

    def shuffle_options(self, correct_answer, possible_answers):
        options = possible_answers + [correct_answer]
        random.shuffle(options)
        return options

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))