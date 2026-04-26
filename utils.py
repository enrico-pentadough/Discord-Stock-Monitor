import discord
import json
import os
import requests
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
def get_stock_price(symbol: str) -> dict | None:
    try:
        url = "https://edge.pse.com.ph/autoComplete/searchCompanyNameSymbol.ax"
        response = requests.post(url, data={"term": symbol.upper()}, headers={
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest"
        })
        results = response.json()
        if not results:
            print(f"Symbol {symbol} not found")
            return None

        company_id = results[0]["companyId"]

        quote_url = f"https://edge.pse.com.ph/companyPage/stockData.do?cmpy_id={company_id}"
        page = requests.get(quote_url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.text, "html.parser")

        price = soup.find("td", string="Last Traded Price")
        if price:
            price = price.find_next_sibling("td").text.strip().replace(",", "")
            return {
                "symbol": symbol.upper(),
                "last_traded_price": float(price)
            }
        print(f"Could not find price for {symbol}")
        return None
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