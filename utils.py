import discord
import json
import os
import aiohttp
from bs4 import BeautifulSoup

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

#Check stocks command
async def get_stock_price(symbol: str) -> dict | None:
    ticker = f"{symbol.upper()}.PS"
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://finance.yahoo.com/",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"Bad response for {symbol}: {response.status}")
                    return None
                data = await response.json()
                quote = data["quoteResponse"]["result"][0]
                price = quote["regularMarketPrice"]
                return {
                    "symbol": symbol.upper(),
                    "last_traded_price": price
                }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

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