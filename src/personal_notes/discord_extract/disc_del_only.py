import os
from dotenv import load_dotenv
import discord
from discord import Intents, Client
from discord.errors import Forbidden
import asyncio

# Load bot token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents
intents = Intents.default()
intents.messages = True

# Define permission flags
PERMISSION_READ_MESSAGES = 1 << 6  # 65536                 uneccessary?
PERMISSION_MANAGE_MESSAGES = 1 << 13  # 8192 uneccessary?
PERMISSION_READ_MESSAGE_HISTORY = 1 << 11  # 73728 uneccessary?
PERMISSION_MANAGE_CHANNELS = 1 << 4  # 16

# Calculate permissions integer
permissions = (
    PERMISSION_READ_MESSAGES | PERMISSION_MANAGE_MESSAGES | 
    PERMISSION_READ_MESSAGE_HISTORY | PERMISSION_MANAGE_CHANNELS
)

# Initialize the Discord client with permissions
client = Client(intents=intents, permissions=permissions)

async def delete_channels(category):
    try:
        # Fetch the channels in the specified category
        channels = category.channels
        for channel in channels:
            # Delete the channel
            await channel.delete()
    except Forbidden as e:
        print(f"Permission error: {e}")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = e.retry_after
            print(f"We are being rate limited. Retrying in {retry_after} seconds.")
            await asyncio.sleep(retry_after)
            await delete_channels(category)
        else:
            print(f"HTTP error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print('Monitoring channels...')
    for guild in client.guilds:
        print(f'Guild: {guild.name}')
        for category in guild.categories:
            if category.name == 'Noble':  # Manually insert category name in the code
                print(f'Category: {category.name}')
                await delete_channels(category)
    await client.close()

# Run the bot
client.run(TOKEN)
