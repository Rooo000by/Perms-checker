import discord
from discord import app_commands
from discord.ext import commands
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

@bot.tree.command(name="perms", description="Show all roles and their permissions on this server")
async def perms(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command must be used inside a server.", ephemeral=True)
        return

    embed = discord.Embed(title=f"Roles and Permissions in {guild.name}", color=discord.Color.blue())

    for role in guild.roles:
        permissions = [perm[0].replace('_', ' ').title() for perm in role.permissions if perm[1]]
        perms_string = ", ".join(permissions) if permissions else "No Permissions"
        embed.add_field(name=role.name, value=perms_string, inline=False)

    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    # Start Flask in a thread
    threading.Thread(target=run_flask).start()

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    bot.run(TOKEN)
