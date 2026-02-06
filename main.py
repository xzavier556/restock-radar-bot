import discord
from discord import app_commands
import requests
import asyncio
import os

# ENV
TOKEN = os.getenv("DISCORD_TOKEN")
ALERT_CHANNEL_ID = int(os.getenv("ALERT_CHANNEL_ID"))

# DISCORD
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# SEARCH URLS
WALMART_URL = "https://www.walmart.com/search?q=pokemon+cards"
TARGET_URL = "https://www.target.com/s?searchTerm=pokemon+cards"
BESTBUY_URL = "https://www.bestbuy.com/site/searchpage.jsp?st=pokemon+cards"

# STORE CHECKERS — RETAIL ONLY
def check_walmart():
    try:
        r = requests.get(WALMART_URL, headers=HEADERS, timeout=10)
        return "Sold & shipped by Walmart" in r.text
    except:
        return False

def check_target():
    try:
        r = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        text = r.text.lower()
        return "sold by target" in text and "out of stock" not in text
    except:
        return False

def check_bestbuy():
    try:
        r = requests.get(BESTBUY_URL, headers=HEADERS, timeout=10)
        return "Sold by Best Buy" in r.text and "Add to Cart" in r.text
    except:
        return False

# SLASH COMMAND — SET ZIP (FIXED)
@tree.command(name="setzip", description="Set your ZIP code for Pokémon restock alerts")
async def setzip(interaction: discord.Interaction, zip: str):
    try:
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        role_name = f"ZIP-{zip}"

        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            role = await guild.create_role(name=role_name)

        await interaction.user.add_roles(role)

        await interaction.followup.send(
            f"✅ ZIP **{zip}** saved. You’ll now get Pokémon restock alerts.",
            ephemeral=True
        )

    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Something went wrong setting your ZIP.",
                ephemeral=True
            )
        print("ZIP ERROR:", e)

# READY EVENT
@client.event
async def on_ready():
    try:
        await tree.sync()
    except:
        pass

    print("🟢 Restock Radar Bot Online")

    channel = client.get_channel(ALERT_CHANNEL_ID)
    await channel.send(
        "🟢 **Restock Radar LIVE**\n"
        "Tracking Pokémon cards:\n"
        "• Walmart (Sold by Walmart)\n"
        "• Target (Sold by Target)\n"
        "• Best Buy (Sold by Best Buy)\n\n"
        "Use `/setzip 12345` to get alerts."
    )

    while True:
        try:
            zip_roles = [r for r in channel.guild.roles if r.name.startswith("ZIP-")]
            pings = " ".join(r.mention for r in zip_roles)

            if check_walmart():
                await channel.send(
                    f"🚨 **WALMART RESTOCK (OFFICIAL)** 🚨\n{pings}\n{WALMART_URL}"
                )
                await asyncio.sleep(1800)

            if check_target():
                await channel.send(
                    f"🚨 **TARGET RESTOCK (OFFICIAL)** 🚨\n{pings}\n{TARGET_URL}"
                )
                await asyncio.sleep(1800)

            if check_bestbuy():
                await channel.send(
                    f"🚨 **BEST BUY RESTOCK (OFFICIAL)** 🚨\n{pings}\n{BESTBUY_URL}"
                )
                await asyncio.sleep(1800)

        except Exception as e:
            print("CHECK ERROR:", e)

        await asyncio.sleep(300)

# RUN
client.run(TOKEN)
