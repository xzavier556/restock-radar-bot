import os
import discord
from discord.ext import tasks
import requests

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("ALERT_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_status = None

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    check_stock.start()

@tasks.loop(minutes=5)
async def check_stock():
    global last_status

    url = "https://www.target.com/p/pokemon-trading-card-game-scarlet-violet-elite-trainer-box/-/A-89444908"
    response = requests.get(url)
    in_stock = "Out of stock" not in response.text

    if last_status is None:
        last_status = in_stock
        return

    if in_stock != last_status:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            status = "🟢 IN STOCK" if in_stock else "🔴 OUT OF STOCK"
            await channel.send(
                f"🚨 **Target Pokémon ETB Update**\n{status}\nCheck fast 👀"
            )
        last_status = in_stock

client.run(TOKEN)
