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
TARGET_SEARCH = "https://www.target.com/s?searchTerm=pokemon+cards"

def check_walmart():
    r = requests.get(WALMART_SEARCH, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    if "Out of stock" not in soup.text:
        return True
    return False

def check_target():
    r = requests.get(TARGET_SEARCH, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    if "out of stock" not in soup.text.lower():
        return True
    return False

@client.event
async def on_ready():
    print("🟢 Restock Radar Bot Online")
    channel = client.get_channel(ALERT_CHANNEL_ID)

    await channel.send("🟢 **Restock Radar is LIVE** — scanning Pokémon cards")

    while True:
        try:
            walmart = check_walmart()
            target = check_target()

            if walmart:
                await channel.send(
                    "🚨 **WALMART RESTOCK** 🚨\nPokémon cards may be IN STOCK:\n"
                    "https://www.walmart.com/search?q=pokemon+cards"
                )
                await asyncio.sleep(1800)

            if target:
                await channel.send(
                    "🚨 **TARGET RESTOCK** 🚨\nPokémon cards may be IN STOCK:\n"
                    "https://www.target.com/s?searchTerm=pokemon+cards"
                )
                await asyncio.sleep(1800)

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(300)  # check every 5 minutes

client.run(TOKEN)
