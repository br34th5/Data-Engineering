import json
import pandas as pd

# After posts are scraped, time to look for duplicates and remove them:
def remove_duplicates(json_file):
    # Read the contents of the JSON file into a list
    with open(json_file, 'r') as file:
        lines = file.readlines()

    # Initialize lists to store message data
    ids = []
    channels = []
    contents = []
    timestamps = []

    # Extract message data from each line in the JSON file
    for line in lines:
        message = json.loads(line)
        message_id = next(iter(message))  # Get the message ID
        ids.append(message_id)
        channels.append(message[message_id]['channel'])
        contents.append(message[message_id]['content'])
        timestamps.append(message[message_id]['timestamp'])

    # Create a DataFrame from the extracted data
    df = pd.DataFrame({'id': ids, 'channel': channels, 'content': contents, 'timestamp': timestamps})

    # Drop duplicates based on message ID
    clean_df = df.drop_duplicates(subset=['id'])

    # Open the new file to save cleaned messages
    with open('clean_messages.json', 'w') as file:
        # Serialize each message individually and write them to the file
        for _, message_row in clean_df.iterrows():
            message_data = {
                'id': message_row['id'],
                'channel': message_row['channel'],
                'content': message_row['content'],
                'timestamp': message_row['timestamp']
            }
            json.dump(message_data, file)
            file.write('\n')  # Add newline for readability

# Example usage:
remove_duplicates('messages.json')