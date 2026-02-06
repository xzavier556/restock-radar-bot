import discord
import requests
from bs4 import BeautifulSoup
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")
ALERT_CHANNEL_ID = int(os.getenv("ALERT_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

WALMART_URL = "https://www.walmart.com/ip/353444924"  # example Pokémon item

def check_walmart():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(WALMART_URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    if "Out of stock" in soup.text:
        return False
    return True

@client.event
async def on_ready():
    print("Bot online")
    channel = client.get_channel(ALERT_CHANNEL_ID)

    while True:
        try:
            in_stock = check_walmart()
            if in_stock:
                await channel.send("🚨 **WALMART RESTOCK ALERT** 🚨\nPokémon cards are IN STOCK!")
                await asyncio.sleep(1800)  # cooldown 30 min
            else:
                print("Still out of stock")
        except Exception as e:
            print(e)

        await asyncio.sleep(300)  # check every 5 min

client.run(TOKEN)
