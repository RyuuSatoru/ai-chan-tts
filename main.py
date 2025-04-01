import os
import discord
import asyncio
import logging
from discord.ext import commands

# Directly define your token and owner ID here
TOKEN = 'MTM1NDEyMjIwMTI0MjI3NTg4Mg.GOaT2b.t_tT9-p5HZfzSV7jItK-moV1ECPmNCS6i0tTEw'  # Replace with your actual token
OWNER_ID = 562536901714903060  # Replace with your actual owner ID
ALLOWED_GUILDS = [1354125046200664116]  # Add your guild IDs here

if not TOKEN:
    raise ValueError("Token không được tìm thấy")
if not OWNER_ID:
    raise ValueError("OWNER_ID không được tìm thấy")

# Thiết lập logging
logging.basicConfig(level=logging.INFO)

# Khởi tạo intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Bật Member Intents
intents.guilds = True  # Bật Guild Intents
intents.bans = True  # Bật Ban Intents
intents.reactions = True  # Bật Reactions Intents

# Khởi tạo bot với prefix là ?
bot = commands.Bot(command_prefix="!", intents=intents)

# Gọi toàn bộ tệp lệnh trong thư mục cogs và các thư mục con, trừ một số tệp không cần thiết
async def load_extensions():
    exclude_files = ['database_utils.py']
    for root, _, files in os.walk("cogs"):
        for filename in files:
            if filename.endswith(".py") and filename != "__init__.py" and filename not in exclude_files:
                cog_path = os.path.join(root, filename)
                cog_name = cog_path.replace(os.sep, ".")[:-3]
                try:
                    await bot.load_extension(cog_name)
                    logging.info(f"Lấy dữ liệu từ tệp: {filename}")
                except Exception as e:
                    logging.error(f"Không lấy được dữ liệu từ tệp {filename}: {e}")

# Sự kiện on_ready
@bot.event
async def on_ready():
    logging.info(f'Bot {bot.user.name} đã sẵn sàng hoạt động!')

# Sự kiện on_member_ban để tự động unban chủ bot
@bot.event
async def on_member_ban(guild, user):
    if user.id == OWNER_ID:
        try:
            await guild.unban(user)
            logging.info(f"Đã unban {user.name} ({user.id})")
        except Exception as e:
            logging.error(f"Lỗi khi unban {user.name} ({user.id}): {e}")

@bot.event
async def on_message(message):
    # Check if the message is a DM
    if isinstance(message.channel, discord.DMChannel):
        # Allow only the specified user to interact in DMs
        if message.author.id != OWNER_ID:
            return
    else:
        # Ignore messages from other guilds
        if message.guild.id not in ALLOWED_GUILDS:
            return
    await bot.process_commands(message)

# Xử lý lỗi quyền hạn cho tất cả các lệnh
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        message = await ctx.send('Bạn không có vai trò yêu cầu để sử dụng lệnh này.')
        await asyncio.sleep(5)
        await message.delete()
    elif isinstance(error, commands.MissingPermissions):
        message = await ctx.send('Bạn không có quyền sử dụng lệnh này!')
        await asyncio.sleep(5)
        await message.delete()
    elif isinstance(error, commands.NotOwner):
        message = await ctx.send('Chỉ chủ sở hữu bot mới có thể sử dụng lệnh này!')
        await asyncio.sleep(5)
        await message.delete()
    elif isinstance(error, commands.CommandNotFound):
        message = await ctx.send('Lệnh không tồn tại.')
        await asyncio.sleep(5)
        await message.delete()
    elif isinstance(error, commands.BotMissingPermissions):
        message = await ctx.send('Bot không có quyền thực hiện lệnh này.')
        await asyncio.sleep(5)
        await message.delete()
    elif isinstance(error, commands.CommandOnCooldown):
        message = await ctx.send(f'Lệnh này đang trong thời gian chờ. Vui lòng thử lại sau {error.retry_after:.2f} giây.')
        await asyncio.sleep(5)
        await message.delete()
    elif isinstance(error, commands.CheckFailure):
        message = await ctx.send('Bạn không đáp ứng các điều kiện để sử dụng lệnh này.')
        await asyncio.sleep(5)
        await message.delete()
    elif isinstance(error, commands.MissingRequiredArgument):
        message = await ctx.send(f'Bạn thiếu đối số bắt buộc: {error.param}. Vui lòng kiểm tra lại cú pháp lệnh.')
        await asyncio.sleep(5)
        await message.delete()
    else:
        logging.error(f"Lỗi xảy ra: {error}")
        raise error

# Chạy BOT
async def main():
    # Kiểm tra và tạo thư mục data nếu không tồn tại
    if not os.path.exists('data'):
        os.makedirs('data')

    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())