import os
import json
import pandas as pd
import re

#next: use regex for <#832925562611302400> format. either show these numbers as letters and tags or don't show at all

# Load the messages from the JSON file
with open('clean_messages.json', 'r', encoding='utf-8') as file:
    messages = [json.loads(line) for line in file]

# Create a DataFrame from the messages
df = pd.DataFrame(messages)

# Sort the DataFrame by 'channel' and 'timestamp'
df.sort_values(by=['channel', 'timestamp'], inplace=True)

# Replace the Discord ID format (<#832925562611302400>) with an empty string or a custom string
def replace_discord_id(content, replacement=''):
    return re.sub(r'<#\d+>', replacement, content)
df['content'] = df['content'].apply(replace_discord_id)

# Group the messages by the 'channel' column
grouped = df.groupby('channel')

# Create a folder to store the text files for categories
os.makedirs('categories', exist_ok=True)

# Iterate over each group (channel)
for channel, group_df in grouped:
    # Get the category of the channel
    category = group_df['category'].iloc[0]  # Assuming 'category' is a column in the DataFrame
    
    # Create a folder for the category if it doesn't exist
    category_folder = os.path.join('categories', category)
    os.makedirs(category_folder, exist_ok=True)
    
    # Create a folder for the channel
    channel_folder = os.path.join(category_folder, channel)
    os.makedirs(channel_folder, exist_ok=True)
    
    # Create a text file for the channel's content
    text_file_path = os.path.join(channel_folder, 'content.txt')
    
    # Write the non-empty content strings to the text file
    with open(text_file_path, 'w', encoding='utf-8') as text_file:
        for content in group_df['content']:
            if content and content != ".":
                text_file.write(content + '\n')
