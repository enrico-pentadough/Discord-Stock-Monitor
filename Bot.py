import discord
import os
import json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from utils import load_data, save_data, send_embed, send_embed_to_saved_users

#THIS PART OF THE CODE HANDLES THE BOT INTERACTING WITH USER WITH SAVE REQUESTS AND DELETE REQUESTS

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

#Saves data into data file
@bot.tree.command(name="save", description="Saves your info", guild=myguild)
@app_commands.describe(
    variable1="Description of variable 1",
    variable2="Description of variable 2"
)
async def save(interaction: discord.Interaction, variable1: str, variable2: str):
    data = load_data()

    user_id = str(interaction.user.id)
    data[user_id] = {
        "mention": interaction.user.mention,
        "variable1": variable1,
        "variable2": variable2
    }

    save_data(data)
    await interaction.response.send_message(
        f"Saved! {interaction.user.mention} — `{variable1}`, `{variable2}`",
        ephemeral=True
    )

#Deletes data in data file
@bot.tree.command(name="remove", description="Removes your saved entry", guild=myguild)
@app_commands.describe(variable1="The variable1 value to remove")
async def remove(interaction: discord.Interaction, variable1: str):
    data = load_data()

    found = None
    for user_id, entry in data.items():
        if entry["variable1"] == variable1:
            found = user_id
            break

    if not found:
        await interaction.response.send_message(
            f"No entry found with `{variable1}`.", ephemeral=True
        )
        return

    del data[found]
    save_data(data)
    await interaction.response.send_message(
        f"Removed entry for `{variable1}`.", ephemeral=True
    )

# Run the bot
bot.run(TOKEN)