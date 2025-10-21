import discord
from discord import app_commands
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.guilds = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync commands globally (or you can restrict to guild for faster updates)
        await self.tree.sync()

bot = MyBot()

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
        # List of permission names for this role where the permission is True
        permissions = [perm[0].replace('_', ' ').title() for perm in role.permissions if perm[1]]
        perms_string = ", ".join(permissions) if permissions else "No Permissions"
        embed.add_field(name=role.name, value=perms_string, inline=False)

    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Set your token as env variable DISCORD_BOT_TOKEN
    bot.run(TOKEN)
