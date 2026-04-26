import discord
import json
import os

#Creates data file if not already existing
DATA_FILE = "data.json"

#Saves data file entries
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)  

#Loads data file entries
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

async def send_embed(target, title: str, description: str, color=discord.Color.blurple()):
    embed = discord.Embed(title=title, description=description, color=color)
    await target.send(embed=embed)

async def send_embed_to_saved_users(bot: discord.Client, title: str, description: str, color=discord.Color.blurple()):
    data = load_data()

    for user_id, entry in data.items():
        try:
            user = await bot.fetch_user(int(user_id))
            await send_embed(user, title, description, color)
        except discord.NotFound:
            print(f"User {user_id} not found, skipping.")
        except discord.Forbidden:
            print(f"User {user_id} has DMs disabled, skipping.")