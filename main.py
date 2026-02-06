import discord
import requests
from bs4 import BeautifulSoup
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")
ALERT_CHANNEL_ID = int(os.getenv("ALERT_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

WALMART_SEARCH = "https://www.walmart.com/search?q=pokemon+cards"
BESTBUY_SEARCH = "https://www.bestbuy.com/site/searchpage.jsp?st=pokemon+cards"

def check_walmart():
    r = requests.get(WALMART_SEARCH, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    # Walmart-only filter
    if "Sold & shipped by Walmart" in soup.text:
        return True
    return False

def check_bestbuy():
    r = requests.get(BESTBUY_SEARCH, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    # Best Buy uses "Add to Cart" when in stock
    if "Add to Cart" in soup.text:
        return True
    return False

@client.event
async def on_ready():
    print("🟢 Restock Radar Bot Online")
    channel = client.get_channel(ALERT_CHANNEL_ID)

    await channel.send(
        "🟢 **Restock Radar LIVE**\n"
        "Tracking Pokémon cards:\n"
        "• Walmart (Sold by Walmart only)\n"
        "• Best Buy"
    )

    while True:
        try:
            if check_walmart():
                await channel.send(
                    "🚨 **WALMART RESTOCK (OFFICIAL)** 🚨\n"
                    "Pokémon cards SOLD BY WALMART are IN STOCK:\n"
                    "https://www.walmart.com/search?q=pokemon+cards"
                )
                await asyncio.sleep(1800)

            if check_bestbuy():
                await channel.send(
                    "🚨 **BEST BUY RESTOCK** 🚨\n"
                    "Pokémon cards may be IN STOCK:\n"
                    "https://www.bestbuy.com/site/searchpage.jsp?st=pokemon+cards"
                )
                await asyncio.sleep(1800)

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(300)  # check every 5 min

client.run(TOKEN)
