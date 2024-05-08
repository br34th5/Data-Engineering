import os
import discord
import json
import asyncio
from dotenv import load_dotenv
from discord import Intents, Client
from discord.errors import Forbidden, HTTPException
import pandas as pd
from collections import deque
import time

#this bot scrapes chosen categories.                                                        !!! manually choose categories

# Load bot token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents
intents = Intents.default()
intents.messages = True

# Define permission flags
PERMISSION_READ_MESSAGES = 1 << 6  # 65536
PERMISSION_MANAGE_MESSAGES = 1 << 13  # 8192
PERMISSION_READ_MESSAGE_HISTORY = 1 << 11  # 73728

# Calculate permissions integer
permissions = PERMISSION_READ_MESSAGES | PERMISSION_MANAGE_MESSAGES | PERMISSION_READ_MESSAGE_HISTORY

# Initialize the Discord client with permissions
client = Client(intents=intents, permissions=permissions)

# Define rate limit settings
RATE_LIMIT_THRESHOLD = 3  # Maximum number of requests per second
RATE_LIMIT_BUCKET = RATE_LIMIT_THRESHOLD  # Initial token bucket capacity
categories_to_monitor = ['Aktualijos']                                                        #!!! manually choose categories

# Initialize request counter
request_count = 0

async def monitor_channel(channel):
    global RATE_LIMIT_BUCKET
    global request_count
    try:
        # Increment request count for each request
        request_count += 1

        # Check if there are enough tokens in the bucket
        if RATE_LIMIT_BUCKET > 0:
            # Make the request
            async for msg in channel.history(limit=None):
                # Create a dictionary to store message data
                message_data = {
                    'id': msg.id,
                    'category': channel.category.name,
                    'channel': channel.name,
                    'content': msg.content,
                    'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M')
                }
                
                # Serialize message data into a string
                message_str = json.dumps({msg.id: message_data})
                
                # Save message data to the file
                with open('messages.json', 'a') as file:
                    file.write(message_str + '\n')  # Write message and add newline for readability
                    
                # Decrement the token bucket
                RATE_LIMIT_BUCKET -= 1
        else:
            # Wait until tokens refill in the bucket
            await asyncio.sleep(1)
            RATE_LIMIT_BUCKET = RATE_LIMIT_THRESHOLD  # Refill the token bucket
            await monitor_channel(channel)

    except Forbidden as e:
        print(f"Permission error: {e}")
    except HTTPException as e:
        # Check if the exception is due to rate limiting
        if e.status == 429:
            retry_after = e.retry_after  #testing
            print(f"We are being rate limited. We could retry in {retry_after} seconds.") #testing
            print(f"We are being rate limited. Exiting for now.")
            await client.close()  # Exit the program
        else:
            print(f"HTTP error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

@client.event
async def on_ready():
    global request_count
    print(f'{client.user} has connected to Discord!')
    print('Monitoring channels...')
    
    # Record the start time
    start_time = time.time()
    
    for guild in client.guilds:
        print(f'Guild: {guild.name}')
        for category in guild.categories:
            if category.name in categories_to_monitor:
                print(f'Category: {category.name}')
                for channel in category.channels:
                    if isinstance(channel, discord.TextChannel):
                        await monitor_channel(channel)
    
    # Calculate and display the elapsed time
    elapsed_time = time.time() - start_time
    print(f"Total requests made: {request_count}")
    print(f"Total time elapsed: {elapsed_time} seconds")
    
    await client.close()

# Run the bot
client.run(TOKEN)


# After posts are scraped, time to look for duplicates and remove them:
def remove_duplicates(json_file):
    # Read the contents of the JSON file into a list
    with open(json_file, 'r') as file:
        lines = file.readlines()

    # Initialize lists to store message data
    ids = []
    category = []
    channels = []
    contents = []
    timestamps = []

    # Extract message data from each line in the JSON file
    for line in lines:
        message = json.loads(line)
        message_id = next(iter(message))  # Get the message ID
        ids.append(message_id)
        category.append(message[message_id]['category']) 
        channels.append(message[message_id]['channel'])
        contents.append(message[message_id]['content'])
        timestamps.append(message[message_id]['timestamp'])

    # Create a DataFrame from the extracted data
    df = pd.DataFrame({'id': ids, 'category': category, 'channel': channels, 'content': contents, 'timestamp': timestamps})

    # Drop duplicates based on message ID
    clean_df = df.drop_duplicates(subset=['id'])

    # Open the file to append cleaned messages
    # Set to store unique message IDs encountered so far
    unique_message_ids = set()

    # Open the file to append cleaned messages
    with open('clean_messages.json', 'a') as file:
        # Read existing messages to populate unique_message_ids set
        with open('clean_messages.json', 'r') as existing_file:
            for line in existing_file:
                try:
                    existing_message = json.loads(line)
                    unique_message_ids.add(existing_message['id'])
                except json.JSONDecodeError as e:
                    print(f"Error loading JSON data: {e}. Skipping this line and continuing.")

        # Serialize each message individually and write them to the file if the ID is not already present
        for _, message_row in clean_df.iterrows():
            message_id = message_row['id']
            if message_id not in unique_message_ids:
                message_data = {
                    'id': message_id,
                    'category': message_row['category'],
                    'channel': message_row['channel'],
                    'content': message_row['content'],
                    'timestamp': message_row['timestamp']
                }
                json.dump(message_data, file)
                file.write('\n')  # Add newline for readability
                unique_message_ids.add(message_id)  # Add the ID to the set of unique IDs



# Example usage:
remove_duplicates('messages.json')
