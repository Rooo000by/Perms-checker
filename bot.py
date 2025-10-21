import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from flask import Flask
import threading
import os

intents = discord.Intents.default()
intents.guilds = True

app = Flask("")

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

class PermsPaginator(View):
    def __init__(self, roles, author):
        super().__init__(timeout=120)
        self.roles = roles
        self.author = author
        self.current_page = 0
        self.roles_per_page = 10
        self.total_pages = (len(roles) - 1) // self.roles_per_page + 1
        self.update_buttons()

    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.total_pages - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your interaction.", ephemeral=True)
            return False
        return True

    def get_page_embed(self):
        embed = discord.Embed(
            title=f"Roles and Permissions (Page {self.current_page + 1}/{self.total_pages})",
            color=discord.Color.blue()
        )
        start = self.current_page * self.roles_per_page
        end = start + self.roles_per_page
        for role in self.roles[start:end]:
            permissions = [perm[0].replace('_', ' ').title() for perm in role.permissions if perm[1]]
            perms_string = ", ".join(permissions) if permissions else "No Permissions"
            embed.add_field(name=role.name, value=perms_string, inline=False)
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

@bot.tree.command(name="perms", description="Show all roles and their permissions on this server")
async def perms(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command must be used inside a server.", ephemeral=True)
        return

    roles = guild.roles
    if len(roles) == 0:
        await interaction.response.send_message("No roles found.", ephemeral=True)
        return

    paginator = PermsPaginator(roles, interaction.user)
    await interaction.response.send_message(embed=paginator.get_page_embed(), view=paginator, ephemeral=True)

if __name__ == "__main__":
    # Start Flask in a thread
    threading.Thread(target=run_flask).start()

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
