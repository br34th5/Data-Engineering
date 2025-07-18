import os
import json
import pandas as pd

# Function to export data into both txt and json files
def export_data(channel, category, content_list):
    # Create a folder for the category if it doesn't exist
    category_folder = os.path.join('categories', category)
    os.makedirs(category_folder, exist_ok=True)
    
    # Create a folder for the channel
    channel_folder = os.path.join(category_folder, channel)
    os.makedirs(channel_folder, exist_ok=True)
    
    # Export content to text file
    text_file_path = os.path.join(channel_folder, 'content.txt')
    with open(text_file_path, 'w', encoding='utf-8') as text_file:
        for content in content_list:
            if content and content != ".":
                text_file.write(content + '\n')

    # Export content to json file
    json_file_path = os.path.join(channel_folder, 'content.json')
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(content_list, json_file, indent=4)

# Load the messages from the JSON file
with open('clean_messages.json', 'r', encoding='utf-8') as file:
    messages = [json.loads(line) for line in file]

# Create a DataFrame from the messages
df = pd.DataFrame(messages)

# Sort the DataFrame by 'channel' and 'timestamp'
df.sort_values(by=['channel', 'timestamp'], inplace=True)

# Group the messages by the 'channel' column
grouped = df.groupby('channel')

# Iterate over each group (channel)
for channel, group_df in grouped:
    # Get the category of the channel
    category = group_df['category'].iloc[0]  # Assuming 'category' is a column in the DataFrame
    
    # Extract content from the group dataframe
    content_list = list(group_df['content'])
    
    # Export data to text and json files
    export_data(channel, category, content_list)
