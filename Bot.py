import discord
import os
import aiohttp
from discord.ext import tasks
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from utils import load_data, save_data, send_embed, get_stock_price

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

@tasks.loop(seconds = 10)  # change to hours=1, seconds=30, etc. For optimal monitoring set to hours=168 for every week notifs
async def check_stocks():
    data = load_data()

    for user_id, entry in data.items():
        symbol = entry["variable1"]
        buy_price = float(entry["variable2"])

        stock = await get_stock_price(symbol)
        if not stock:
            continue

        current_price = stock["last_traded_price"]
        change = current_price - buy_price
        percent_change = (change / buy_price) * 100

        user = await bot.fetch_user(int(user_id))
        await send_embed(
            user,
            f"📊 {symbol} Update",
            f"**Buy price:** ₱{buy_price}\n"
            f"**Current price:** ₱{current_price}\n"
            f"**Change:** ₱{change:+.2f} ({percent_change:+.2f}%)"
        )

@bot.event
async def on_ready():
    await bot.tree.sync(guild=myguild)
    try: 
        check_stocks.start()  
    except Exception as e:
        print(f"Error when attempting to run loop")
        return None
    print(f"Logged in as {bot.user} and synced slash commands!")

@bot.tree.command(name="ping", description="test", guild=myguild)
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

#Saves data into data file
@bot.tree.command(name="track", description="Starts tracking the price of a specified stock", guild=myguild)
@app_commands.describe(
    variable1="The stock you want to start monitoring",
    variable2="The value at which you bought it"
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
        f"Tracking! {interaction.user.mention} — `{variable1}`, `{variable2}`",
        ephemeral=True
    )

#Deletes data in data file
@bot.tree.command(name="untrack", description="Untracks a Monitored Stock", guild=myguild)
@app_commands.describe(variable1="The stock you no longer want to monitor")
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
        f"No longer tracking `{variable1}`.", ephemeral=True
    )


# Run the bot
bot.run(TOKEN)