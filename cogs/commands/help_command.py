import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.paginator = None

    def paginate(self, mapping, ctx, commands_per_page=7):
        embeds = []
        game_commands = []
        voice_commands = []
        everyone_commands = []
        admin_commands = []

        prefix = ctx.clean_prefix

        # Phân loại các lệnh
        for cog, command_list in mapping.items():
            for command in command_list:
                command_info = f'`{prefix}{command.name}`: {command.help}'
                if command.name in ["3cay", "lamviec", "chanle", "nhanqua", "vaytien", "trano", "balance", "give", "top", "topnotien", "shopbds", "shophc", "muabds", "banbds", "muahc"]:
                    game_commands.append(command_info)
                elif command.name in ["play", "addpl", "deletepl", "createpl", "getpl", "pause", "resume", "join", "leave", "vs", "loop", "unloop", "previous", "skip"]:
                    voice_commands.append(command_info)
                elif command.name in ["bcc", "cmt", "kt"]:  # Thêm lệnh bcc, cmt và kt vào danh sách lệnh cho mọi người
                    everyone_commands.append(command_info)
                elif any(check for check in command.checks):
                    admin_commands.append(command_info)
                else:
                    everyone_commands.append(command_info)
        
        # Sắp xếp các lệnh theo tên
        game_commands_sorted = sorted(game_commands)
        voice_commands_sorted = sorted(voice_commands)
        everyone_commands_sorted = sorted(everyone_commands)
        admin_commands_sorted = sorted(admin_commands)
        
        # Chia danh sách lệnh thành các trang
        def create_chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        game_command_chunks = list(create_chunks(game_commands_sorted, commands_per_page))
        voice_command_chunks = list(create_chunks(voice_commands_sorted, commands_per_page))
        everyone_command_chunks = list(create_chunks(everyone_commands_sorted, commands_per_page))
        admin_command_chunks = list(create_chunks(admin_commands_sorted, commands_per_page))

        # Tạo Embed cho lệnh game
        for index, chunk in enumerate(game_command_chunks):
            description = '\n\n'.join(chunk)
            embed = discord.Embed(
                title="Danh sách các lệnh game",
                description=description,
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Trang {index + 1} / {len(game_command_chunks) + len(voice_command_chunks) + len(everyone_command_chunks) + len(admin_command_chunks)}")
            embeds.append(embed)

        # Tạo Embed cho lệnh voice
        for index, chunk in enumerate(voice_command_chunks):
            description = '\n\n'.join(chunk)
            embed = discord.Embed(
                title="Danh sách các lệnh voice",
                description=description,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Trang {index + 1 + len(game_command_chunks)} / {len(game_command_chunks) + len(voice_command_chunks) + len(everyone_command_chunks) + len(admin_command_chunks)}")
            embeds.append(embed)

        # Tạo Embed cho lệnh dành cho mọi người
        for index, chunk in enumerate(everyone_command_chunks):
            description = '\n\n'.join(chunk)
            embed = discord.Embed(
                title="Danh sách các lệnh cho mọi người",
                description=description,
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Trang {index + 1 + len(game_command_chunks) + len(voice_command_chunks)} / {len(game_command_chunks) + len(voice_command_chunks) + len(everyone_command_chunks) + len(admin_command_chunks)}")
            embeds.append(embed)
        
        # Tạo Embed cho lệnh dành cho admin
        for index, chunk in enumerate(admin_command_chunks):
            description = '\n\n'.join(chunk)
            embed = discord.Embed(
                title="Danh sách các lệnh cho admin",
                description=description,
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Trang {index + 1 + len(game_command_chunks) + len(voice_command_chunks) + len(everyone_command_chunks)} / {len(game_command_chunks) + len(voice_command_chunks) + len(everyone_command_chunks) + len(admin_command_chunks)}")
            embeds.append(embed)

        return embeds

    async def send_bot_help(self, mapping):
        ctx = self.context
        embeds = self.paginate(mapping, ctx)
        if not embeds:
            await ctx.send("Không có lệnh nào được đăng ký.")
            return
        view = HelpPaginator(embeds)
        first_embed = embeds[0]
        message = await ctx.send(embed=first_embed, view=view)
        await asyncio.sleep(120)  # Đợi 2 phút
        await message.delete()

class HelpPaginator(View):
    def __init__(self, embeds):
        super().__init__(timeout=120)
        self.embeds = embeds
        self.current_page = 0

        # Khởi tạo nút điều hướng
        self.prev_button = Button(style=discord.ButtonStyle.primary, label="◀️ Trang Trước Đó", disabled=True)
        self.next_button = Button(style=discord.ButtonStyle.primary, label="Trang Kế Tiếp ▶️", disabled=(len(self.embeds) <= 1))
        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page
        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    async def prev_page(self, interaction: discord.Interaction):
        self.current_page -= 1
        if self.current_page == 0:
            self.prev_button.disabled = True
        self.next_button.disabled = False
        embed = self.embeds[self.current_page]
        embed.set_footer(text=f"Trang {self.current_page + 1} / {len(self.embeds)}")
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_page(self, interaction: discord.Interaction):
        self.current_page += 1
        if self.current_page == len(self.embeds) - 1:
            self.next_button.disabled = True
        self.prev_button.disabled = False
        embed = self.embeds[self.current_page]
        embed.set_footer(text=f"Trang {self.current_page + 1} / {len(self.embeds)}")
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    bot.help_command = CustomHelpCommand()