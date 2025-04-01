import os
import json
import discord
from discord.ext import commands

def has_permissions_or_owner(**perms):
    async def predicate(ctx):
        if ctx.author.id == ctx.bot.owner_id:
            return True
        resolved = ctx.channel.permissions_for(ctx.author)
        return all(getattr(resolved, name, None) == value for name, value in perms.items())
    return commands.check(predicate)

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_listener(self.on_raw_reaction_add, 'on_raw_reaction_add')
        self.bot.add_listener(self.on_raw_reaction_remove, 'on_raw_reaction_remove')
        self.reaction_roles = self.load_reaction_role_data()

    def load_reaction_role_data(self):
        file_path = "data/reaction_roles.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return {}

    def save_reaction_role_data(self):
        file_path = "data/reaction_roles.json"
        with open(file_path, "w") as f:
            json.dump(self.reaction_roles, f, indent=4)

    @commands.command()
    @has_permissions_or_owner(administrator=True)
    async def setup(self, ctx, option=None):
        """Tạo Log - Server để kiểm tra các sự kiện server."""
        if option not in ["log", "reactionrole", "announcement", "welcome", "mainchat", "all"]:
            embed = discord.Embed(
                title="Lỗi",
                description="Vui lòng chọn một trong các tùy chọn: log, reactionrole, announcement, welcome, mainchat, all",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        guild = ctx.guild  # Lấy server từ context

        # Đảm bảo thư mục data tồn tại
        if not os.path.exists("data"):
            os.makedirs("data")

        # Đọc tệp JSON hiện có
        try:
            with open("data/channel_ids.json", "r") as f:
                all_channel_data = json.load(f)
        except FileNotFoundError:
            all_channel_data = {}

        guild_data = all_channel_data.get(str(guild.id), {})

        # Kiểm tra và xóa các danh mục và kênh bên trong nếu đã tồn tại và được tạo bởi lệnh setup trước đó
        async def delete_category_if_exists(category_id):
            if category_id:
                category = discord.utils.get(guild.categories, id=category_id)
                if category:
                    for channel in category.channels:
                        await channel.delete()
                    await category.delete()

        if option in ["log", "all"]:
            await delete_category_if_exists(guild_data.get("log_category_id"))
        if option in ["reactionrole", "all"]:
            await delete_category_if_exists(guild_data.get("important_category_id"))
        if option in ["announcement", "all"]:
            await delete_category_if_exists(guild_data.get("announcement_category_id"))
        if option in ["welcome", "all"]:
            await delete_category_if_exists(guild_data.get("welcome_category_id"))
        if option in ["mainchat", "all"]:
            await delete_category_if_exists(guild_data.get("general_category_id"))
        
        # Xóa vai trò nếu đã tồn tại
        if option in ["all"]:
            member_role_id = guild_data.get("member_role_id")
            if member_role_id:
                member_role = guild.get_role(member_role_id)
                if member_role:
                    await member_role.delete()

        embed = discord.Embed(
            title="Thông báo",
            description="Đang tạo các danh mục và kênh mới...",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

        # Thiết lập vai trò "Member" để hiển thị riêng biệt với các thành viên trực tuyến
        try:
            member_role = discord.utils.get(guild.roles, name="Member")
            if member_role is None:
                member_role = await guild.create_role(
                    name="Member",
                    color=discord.Color(0x18d32c),
                    hoist=True,  # Hiển thị vai trò riêng biệt với các thành viên trực tuyến
                    permissions=discord.Permissions(
                        view_channel=True,
                        send_messages=True,
                        add_reactions=True,
                        use_external_stickers=True,
                        use_external_emojis=True,
                        send_tts_messages=True,
                        read_message_history=True,
                        connect=True,
                        speak=True,
                        stream=True,
                        use_voice_activation=True,
                        priority_speaker=True,
                        view_guild_insights=True
                    )
                )
            else:
                await member_role.edit(hoist=True)  # Cập nhật nếu vai trò đã tồn tại
        except Exception as e:
            embed = discord.Embed(
                title="Lỗi",
                description=f"Lỗi khi tạo vai trò Member: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Tạo danh mục welcome-server (trên cùng)
        if option in ["welcome", "all"]:
            try:
                welcome_category = await guild.create_category_channel(
                    name="👋 welcome-server",
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=False,
                            read_message_history=True,
                            connect=False
                        ),
                    }
                )
                # Đẩy danh mục lên trên đầu
                await welcome_category.edit(position=0)

                # Tạo các kênh trong danh mục welcome-server
                welcome_channel = await guild.create_text_channel(
                    name="welcome",
                    category=welcome_category
                )
                goodbye_channel = await guild.create_text_channel(
                    name="goodbye",
                    category=welcome_category
                )
                booster_server_channel = await guild.create_text_channel(
                    name="booster-server",
                    category=welcome_category
                )
            except Exception as e:
                embed = discord.Embed(
                    title="Lỗi",
                    description=f"Lỗi khi tạo danh mục và kênh trong welcome-server: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        # Tạo danh mục important (cùng quyền với welcome)
        if option in ["reactionrole", "all"]:
            try:
                important_category = await guild.create_category_channel(
                    name="‼️ important",
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=False,
                            read_message_history=True,
                            connect=False
                        ),
                    }
                )
                # Đẩy danh mục lên vị trí thứ 2
                await important_category.edit(position=1)

                # Tạo các kênh trong danh mục important
                rule_channel = await guild.create_text_channel(
                    name="luật",
                    category=important_category
                )
                get_permission_channel = await guild.create_text_channel(
                    name="lấy quyền truy cập",
                    category=important_category
                )
            except Exception as e:
                embed = discord.Embed(
                    title="Lỗi",
                    description=f"Lỗi khi tạo danh mục và kênh trong important: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        # Tạo danh mục Thông báo (dưới danh mục important)
        if option in ["announcement", "all"]:
            try:
                announcement_category = await guild.create_category_channel(
                    name="🔊 Thông báo",
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(
                            view_channel=False
                        ),
                        member_role: discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=False,
                            read_message_history=True
                        ),
                    }
                )
                # Đẩy danh mục xuống dưới danh mục important
                await announcement_category.edit(position=2)

                # Tạo các kênh trong danh mục Thông báo
                announcement_channel = await guild.create_text_channel(
                    name="Thông báo",
                    category=announcement_category
                )
                link_invite_channel = await guild.create_text_channel(
                    name="link invite server",
                    category=announcement_category
                )
                event_channel = await guild.create_text_channel(
                    name="sự kiện",
                    category=announcement_category
                )

                # Kiểm tra xem liên kết mời đã tồn tại hay chưa
                invite_link = guild_data.get("invite_link")
                if not invite_link:
                    invite_link = await guild.text_channels[0].create_invite(max_age=0, max_uses=0, unique=True)
                    guild_data["invite_link"] = str(invite_link)

                embed = discord.Embed(
                    title="Server Invite Link",
                    description=f"Here is a permanent invite link to our server: [Invite Link]({invite_link})",
                    color=discord.Color.blue()
                )
                await link_invite_channel.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(
                    title="Lỗi",
                    description=f"Lỗi khi tạo danh mục và kênh trong Thông báo: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        # Tạo danh mục sảnh chung (ở giữa)
        if option in ["mainchat", "all"]:
            try:
                general_category = await guild.create_category_channel(
                    name="sảnh chung",
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(
                            view_channel=False
                        ),
                        member_role: discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True,
                            add_reactions=True,
                            use_external_stickers=True,
                            use_external_emojis=True,
                            send_tts_messages=True,
                            read_message_history=True,
                            connect=True,
                            speak=True,
                            stream=True,
                            use_voice_activation=True,
                            priority_speaker=True,
                            view_guild_insights=True
                        ),
                    }
                )
                # Đẩy danh mục lên vị trí giữa
                await general_category.edit(position=3)

                # Tạo các kênh trong danh mục sảnh chung
                general_chat_channel = await guild.create_text_channel(
                    name="chat tổng",
                    category=general_category
                )
                bot_command_channel = await guild.create_text_channel(
                    name="bot command",
                    category=general_category
                )
            except Exception as e:
                embed = discord.Embed(
                    title="Lỗi",
                    description=f"Lỗi khi tạo danh mục và kênh trong sảnh chung: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        # Tạo danh mục LOG - SERVER (ở dưới cùng)
        if option in ["log", "all"]:
            try:
                log_category = await guild.create_category_channel(
                    name="📝 LOG - SERVER",
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(
                            view_channel=False,
                            send_messages=False,
                            read_message_history=False,
                            connect=False
                        ),
                    }
                )
                # Đẩy danh mục xuống dưới cùng
                await log_category.edit(position=len(guild.categories))

                # Tạo các kênh trong danh mục LOG - SERVER
                ban_status_channel = await guild.create_text_channel(
                    name="ban-status",
                    category=log_category
                )
                member_update_channel = await guild.create_text_channel(
                    name="member-update",
                    category=log_category
                )
                server_update_channel = await guild.create_text_channel(
                    name="server-update",
                    category=log_category
                )
                message_update_channel = await guild.create_text_channel(
                    name="message-update",
                    category=log_category
                )
                member_voice_channel = await guild.create_voice_channel(
                    name="👾 Thành Viên:",
                    category=log_category
                )
                bots_voice_channel = await guild.create_voice_channel(
                    name="👾 Bots:",
                    category=log_category
                )
            except Exception as e:
                embed = discord.Embed(
                    title="Lỗi",
                    description=f"Lỗi khi tạo danh mục và kênh trong LOG - SERVER: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        # Cập nhật hoặc thêm dữ liệu cho server hiện tại
        if option in ["all"]:
            channel_data = {
                "log_category_id": log_category.id,
                "welcome_category_id": welcome_category.id,
                "important_category_id": important_category.id,
                "announcement_category_id": announcement_category.id,
                "general_category_id": general_category.id,
                "welcome_channel_id": welcome_channel.id,
                "goodbye_channel_id": goodbye_channel.id,
                "booster_server_channel_id": booster_server_channel.id,
                "rule_channel_id": rule_channel.id,
                "get_permission_channel_id": get_permission_channel.id,
                "announcement_channel_id": announcement_channel.id,
                "link_invite_channel_id": link_invite_channel.id,
                "event_channel_id": event_channel.id,
                "ban_status_channel_id": ban_status_channel.id,
                "member_update_channel_id": member_update_channel.id,
                "server_update_channel_id": server_update_channel.id,
                "message_update_channel_id": message_update_channel.id,
                "member_voice_channel_id": member_voice_channel.id,
                "bots_voice_channel_id": bots_voice_channel.id,
                "general_chat_channel_id": general_chat_channel.id,
                "bot_command_channel_id": bot_command_channel.id,
                "member_role_id": member_role.id,
                "invite_link": guild_data.get("invite_link")
            }
        elif option == "log":
            channel_data = {
                "log_category_id": log_category.id,
                "ban_status_channel_id": ban_status_channel.id,
                "member_update_channel_id": member_update_channel.id,
                "server_update_channel_id": server_update_channel.id,
                "message_update_channel_id": message_update_channel.id,
                "member_voice_channel_id": member_voice_channel.id,
                "bots_voice_channel_id": bots_voice_channel.id,
            }
        elif option == "reactionrole":
            channel_data = {
                "important_category_id": important_category.id,
                "rule_channel_id": rule_channel.id,
                "get_permission_channel_id": get_permission_channel.id,
            }
        elif option == "announcement":
            channel_data = {
                "announcement_category_id": announcement_category.id,
                "announcement_channel_id": announcement_channel.id,
                "link_invite_channel_id": link_invite_channel.id,
                "event_channel_id": event_channel.id,
                "invite_link": guild_data.get("invite_link")
            }
        elif option == "welcome":
            channel_data = {
                "welcome_category_id": welcome_category.id,
                "welcome_channel_id": welcome_channel.id,
                "goodbye_channel_id": goodbye_channel.id,
                "booster_server_channel_id": booster_server_channel.id,
            }
        elif option == "mainchat":
            channel_data = {
                "general_category_id": general_category.id,
                "general_chat_channel_id": general_chat_channel.id,
                "bot_command_channel_id": bot_command_channel.id,
            }
        all_channel_data[str(guild.id)] = channel_data

        # Lưu trữ thông tin đã cập nhật vào tệp JSON
        try:
            with open("data/channel_ids.json", "w") as f:
                json.dump(all_channel_data, f, indent=4)
        except Exception as e:
            embed = discord.Embed(
                title="Lỗi",
                description=f"Lỗi khi lưu ID kênh vào tệp: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="Setup Log Server",
            description="Đã cài đặt toàn bộ Log Server !!!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        # Cập nhật số lượng member và bot sau khi tạo kênh
        if option in ["log", "all"]:
            member_count = len([member for member in guild.members if not member.bot])
            bot_count = len([member for member in guild.members if member.bot])

            try:
                await member_voice_channel.edit(name=f"👾 Thành Viên: {member_count}")
                await bots_voice_channel.edit(name=f"👾 Bots: {bot_count}")
            except Exception as e:
                embed = discord.Embed(
                    title="Lỗi",
                    description=f"Lỗi khi cập nhật tên kênh voice: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

        # Gửi tin nhắn "hello" vào kênh lấy quyền truy cập và thêm reaction
        if option in ["reactionrole", "all"]:
            try:
                permission_message = await get_permission_channel.send("Vui lòng bấm icon bên dưới để nhận quyền truy cập vào server||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||____||@everyone")
                await permission_message.add_reaction("✅")

                # Lưu trữ ID của tin nhắn để sử dụng trong sự kiện phản ứng
                channel_data["permission_message_id"] = permission_message.id
                with open("data/channel_ids.json", "w") as f:
                    json.dump(all_channel_data, f, indent=4)
            except Exception as e:
                embed = discord.Embed(
                    title="Lỗi",
                    description=f"Lỗi khi gửi tin nhắn vào kênh lấy quyền truy cập: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

    @commands.command(help="Thêm vai trò dựa trên phản ứng\nCú pháp: ?reactionrole <message_link_or_id> <role> <emoji>")
    @commands.has_permissions(manage_roles=True)
    async def reactionrole(self, ctx, message_identifier: str, role: discord.Role, emoji: str):
        try:
            if message_identifier.isdigit():
                message_id = int(message_identifier)
                message = None

                for channel in ctx.guild.text_channels:
                    try:
                        message = await channel.fetch_message(message_id)
                        if message:
                            break
                    except discord.NotFound:
                        continue

                if not message:
                    await ctx.send("Không tìm thấy tin nhắn với ID cung cấp.")
                    return
            else:
                parts = message_identifier.split('/')
                if len(parts) < 7:
                    await ctx.send("Liên kết tin nhắn không hợp lệ.")
                    return
                guild_id = int(parts[4])
                channel_id = int(parts[5])
                message_id = int(parts[6])

                if guild_id != ctx.guild.id:
                    await ctx.send("Liên kết tin nhắn không thuộc server này.")
                    return

                channel = self.bot.get_channel(channel_id)
                if channel is None:
                    await ctx.send("Không tìm thấy kênh.")
                    return

                message = await channel.fetch_message(message_id)
                if message is None:
                    await ctx.send("Không tìm thấy tin nhắn.")
                    return

            await message.add_reaction(emoji)

            if message_id not in self.reaction_roles:
                self.reaction_roles[message_id] = []
            self.reaction_roles[message_id].append((role.id, str(emoji)))
            self.save_reaction_role_data()

            await ctx.send(f"Đã thêm vai trò {role.name} với phản ứng {emoji} vào tin nhắn.")
        
        except discord.Forbidden:
            await ctx.send("Bot không có quyền để thêm phản ứng vào tin nhắn này.")
        except Exception as e:
            await ctx.send(f"Đã xảy ra lỗi: {e}")

    async def on_raw_reaction_add(self, payload):
        """Sự kiện khi có ai đó thêm phản ứng vào tin nhắn."""
        if payload.member.bot:
            return

        # Đảm bảo thư mục data tồn tại
        if not os.path.exists("data"):
            return

        # Đọc tệp JSON hiện có
        try:
            with open("data/channel_ids.json", "r") as f:
                all_channel_data = json.load(f)
        except FileNotFoundError:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        guild_data = all_channel_data.get(str(guild.id))
        if not guild_data:
            return

        if payload.message_id == guild_data.get("permission_message_id"):
            member_role = guild.get_role(guild_data["member_role_id"])
            if not member_role:
                return

            member = guild.get_member(payload.user_id)
            if not member:
                return

            try:
                await member.add_roles(member_role)
            except Exception as e:
                print(f"Failed to add role: {e}")

        # Kiểm tra phản ứng cho các vai trò dựa trên phản ứng
        if payload.message_id in self.reaction_roles:
            role_info = next((r for r in self.reaction_roles[payload.message_id] if r[1] == str(payload.emoji)), None)
            if role_info:
                role = guild.get_role(role_info[0])
                if role:
                    member = guild.get_member(payload.user_id)
                    if member and role not in member.roles:
                        await member.add_roles(role)
                        print(f"Đã cấp vai trò {role.name} cho {member.name}")

    async def on_raw_reaction_remove(self, payload):
        """Sự kiện khi có ai đó bỏ phản ứng khỏi tin nhắn."""
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        # Đảm bảo thư mục data tồn tại
        if not os.path.exists("data"):
            return

        # Đọc tệp JSON hiện có
        try:
            with open("data/channel_ids.json", "r") as f:
                all_channel_data = json.load(f)
        except FileNotFoundError:
            return

        guild_data = all_channel_data.get(str(guild.id))
        if not guild_data:
            return

        if payload.message_id == guild_data.get("permission_message_id"):
            member_role = guild.get_role(guild_data["member_role_id"])
            if not member_role:
                return

            member = guild.get_member(payload.user_id)
            if not member:
                return

            try:
                await member.remove_roles(member_role)
            except Exception as e:
                print(f"Failed to remove role: {e}")

        # Kiểm tra phản ứng cho các vai trò dựa trên phản ứng
        if payload.message_id in self.reaction_roles:
            role_info = next((r for r in self.reaction_roles[payload.message_id] if r[1] == str(payload.emoji)), None)
            if role_info:
                role = guild.get_role(role_info[0])
                if role:
                    member = guild.get_member(payload.user_id)
                    if member and role in member.roles:
                        await member.remove_roles(role)
                        print(f"Đã xóa vai trò {role.name} khỏi {member.name}")

    @setup.error
    async def setup_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Lỗi",
                description="Bạn không có quyền để thực hiện lệnh này.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Lỗi",
                description=f"Đã xảy ra lỗi: {error}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Setup(bot))