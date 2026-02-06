import discord
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import asyncio
import os

# ENV VARIABLES (Railway)
TOKEN = os.getenv("DISCORD_TOKEN")
ALERT_CHANNEL_ID = int(os.getenv("ALERT_CHANNEL_ID"))

# DISCORD SETUP
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# HEADERS FOR REQUESTS
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# SEARCH URLS
WALMART_URL = "https://www.walmart.com/search?q=pokemon+cards"
TARGET_URL = "https://www.target.com/s?searchTerm=pokemon+cards"
BESTBUY_URL = "https://www.bestbuy.com/site/searchpage.jsp?st=pokemon+cards"

# STORE CHECKERS
def check_walmart():
    try:
        r = requests.get(WALMART_URL, headers=HEADERS, timeout=10)
        return "Sold & shipped by Walmart" in r.text
    except:
        return False

def check_target():
    try:
        r = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        return "out of stock" not in r.text.lower()
    except:
        return False

def check_bestbuy():
    try:
        r = requests.get(BESTBUY_URL, headers=HEADERS, timeout=10)
        return "Add to Cart" in r.text
    except:
        return False

# SLASH COMMAND — SET ZIP
@tree.command(name="setzip", description="Set your ZIP code for Pokémon restock alerts")
async def setzip(interaction: discord.Interaction, zip: str):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    role_name = f"ZIP-{zip}"

    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        role = await guild.create_role(name=role_name)

    await interaction.user.add_roles(role)

    await interaction.followup.send(
        f"✅ ZIP set to **{zip}**. You’ll receive Pokémon restock alerts.",
        ephemeral=True
    )

# BOT READY EVENT
@client.event
async def on_ready():
    await tree.sync()
    print("🟢 Restock Radar Bot Online")

    channel = client.get_channel(ALERT_CHANNEL_ID)
    await channel.send(
        "🟢 **Restock Radar LIVE**\n"
        "Tracking Pokémon cards at:\n"
        "• Walmart (Sold by Walmart only)\n"
        "• Target\n"
        "• Best Buy\n\n"
        "Use `/setzip 12345` to get alerts."
    )

    while True:
        try:
            zip_roles = [r for r in channel.guild.roles if r.name.startswith("ZIP-")]
            pings = " ".join(r.mention for r in zip_roles)

            if check_walmart():
                await channel.send(
                    f"🚨 **WALMART RESTOCK (OFFICIAL)** 🚨\n"
                    f"{pings}\n"
                    f"https://www.walmart.com/search?q=pokemon+cards"
                )
                await asyncio.sleep(1800)

            if check_target():
                await channel.send(
                    f"🚨 **TARGET RESTOCK** 🚨\n"
                    f"{pings}\n"
                    f"https://www.target.com/s?searchTerm=pokemon+cards"
                )
                await asyncio.sleep(1800)

            if check_bestbuy():
                await channel.send(
                    f"🚨 **BEST BUY RESTOCK** 🚨\n"
                    f"{pings}\n"
                    f"https://www.bestbuy.com/site/searchpage.jsp?st=pokemon+cards"
                )
                await asyncio.sleep(1800)

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(300)  # check every 5 minutes

# RUN BOT
client.run(TOKEN)
