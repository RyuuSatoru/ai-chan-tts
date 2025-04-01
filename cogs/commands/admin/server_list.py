import json
import discord
from discord.ext import commands
from discord.ui import View, Button
import os

class ServerList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_links = self.load_invite_links()

    def load_invite_links(self):
        if os.path.exists('data/channel_ids.json'):
            with open('data/channel_ids.json', 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_invite_links(self):
        with open('data/channel_ids.json', 'w') as f:
            json.dump(self.invite_links, f, indent=4)

    async def create_or_get_invite(self, guild):
        if str(guild.id) in self.invite_links and "invite_url" in self.invite_links[str(guild.id)]:
            invite_url = self.invite_links[str(guild.id)]["invite_url"]
            # Check if the invite link is still valid
            try:
                invites = await guild.invites()
                for invite in invites:
                    if invite.url == invite_url:
                        return invite_url
            except Exception as e:
                print(f"Error checking invite: {e}")
        
        # Create a new invite link
        try:
            invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=0)
            if str(guild.id) not in self.invite_links:
                self.invite_links[str(guild.id)] = {}
            self.invite_links[str(guild.id)]["invite_url"] = invite.url
            self.save_invite_links()
            return invite.url
        except Exception as e:
            return f"Lỗi khi tạo lời mời: {e}"

    @commands.command(name="listserver", help="Hiển thị danh sách server mà bot đang hỗ trợ")
    @commands.has_permissions(administrator=True)
    async def listserver(self, ctx):
        servers = []
        for guild in self.bot.guilds:
            try:
                invite_url = await self.create_or_get_invite(guild)
                owner = guild.owner
                server_info = {
                    "name": guild.name,
                    "id": guild.id,
                    "owner_mention": owner.mention,
                    "owner_id": owner.id,
                    "invite_url": invite_url
                }
                servers.append(server_info)
            except Exception as e:
                server_info = {
                    "name": guild.name,
                    "id": guild.id,
                    "owner_mention": "N/A",
                    "owner_id": "N/A",
                    "invite_url": f"Lỗi khi tạo lời mời: {e}"
                }
                servers.append(server_info)

        await ctx.message.delete()  # Xóa lệnh trước khi gửi thông tin
        await self.send_server_list(ctx, servers, page=0)

    async def send_server_list(self, ctx, servers, page):
        items_per_page = 5
        start = page * items_per_page
        end = start + items_per_page
        embed = discord.Embed(title="Danh sách BOT đang hỗ trợ các Server", color=discord.Color.blue())

        for idx, server in enumerate(servers[start:end], start=start + 1):
            embed.add_field(
                name=f"{idx}. Server: {server['name']}",
                value=(
                    f"ID Server: {server['id']}\n"
                    f"Chủ server: {server['owner_mention']}\n"
                    f"ID Chủ server: {server['owner_id']}\n"
                    f"[Link tham gia]({server['invite_url']})"
                ),
                inline=False
            )

        view = ServerListView(ctx, servers, page)
        message = await ctx.send(embed=embed, view=view)
        view.message = message
        await message.delete(delay=300)

class ServerListView(View):
    def __init__(self, ctx, servers, page):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.servers = servers
        self.page = page
        self.message = None  # Initialize the message attribute

        # Khởi tạo nút điều hướng
        self.prev_button = Button(style=discord.ButtonStyle.primary, label="◀️ Trang Trước", disabled=(self.page == 0))
        self.next_button = Button(style=discord.ButtonStyle.primary, label="Trang Tiếp ▶️", disabled=(self.page >= (len(self.servers) - 1) // 5))
        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page
        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    async def prev_page(self, interaction: discord.Interaction):
        self.page -= 1
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page >= (len(self.servers) - 1) // 5
        await self.update_message(interaction)

    async def next_page(self, interaction: discord.Interaction):
        self.page += 1
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page >= (len(self.servers) - 1) // 5
        await self.update_message(interaction)

    async def update_message(self, interaction):
        embed = discord.Embed(title="Danh sách BOT đang hỗ trợ các Server", color=discord.Color.blue())
        start = self.page * 5
        end = start + 5

        for idx, server in enumerate(self.servers[start:end], start=start + 1):
            embed.add_field(
                name=f"{idx}. Server: {server['name']}",
                value=(
                    f"ID Server: {server['id']}\n"
                    f"Chủ server: {server['owner_mention']}\n"
                    f"ID Chủ server: {server['owner_id']}\n"
                    f"[Link tham gia]({server['invite_url']})"
                ),
                inline=False
            )

        await interaction.response.edit_message(embed=embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
            await self.message.delete(delay=1)
        except discord.errors.NotFound:
            print("Message not found, it might have been deleted already.")

async def setup(bot):
    await bot.add_cog(ServerList(bot))