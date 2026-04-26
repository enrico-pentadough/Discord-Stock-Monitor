import discord
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

#imports tokens and IDs from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ID = os.getenv("GUILD_ID")

#declares intents of the bot
intents = discord.Intents.default()
intents.message_content = True


myguild = discord.Object(id=int(ID))

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=myguild)
    print(f"Logged in as {bot.user} and synced slash commands!")

@bot.tree.command(name="ping", description="test", guild=myguild)
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

# Run the bot
bot.run(TOKEN)