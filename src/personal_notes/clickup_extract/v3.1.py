import os
import pandas as pd
import re

#output looks like: with unnecessary folders by the tags,  clean data. 


# Preparing clickup exported CSV file for cleaning unnecessary columns
csv_file = 'clickup2.csv'  # Replace with the path to your CSV file
df = pd.read_csv(csv_file)

# Specify the columns you want to delete (excluding "Task ID" and "Parent ID")
columns_to_delete = ['Attachments', 'Date Created', 'Date Created Text', 'Due Date', 'Due Date Text',
                     'Start Date', 'Start Date Text', 'Assignees', 'Folder Name', 'Time Estimated',
                     'Time Estimated Text', 'Checklists', 'Comments', 'Assigned Comments', 'Time Spent',
                     'Time Spent Text', 'Rolled Up Time', 'Rolled Up Time Text', 'Priority', 'Status']

# Drop the specified columns from the DataFrame
df = df.drop(columns=columns_to_delete)

# Sort the DataFrame by the "Space Name" column
df_sorted = df.sort_values(by='Space Name')

# Get all unique values in the "List Name" column
unique_values = df_sorted['List Name'].unique()

# Print or use the unique values as needed
print(unique_values)

# Find all unique tags
all_tags = set()
for tags in df_sorted['Tags'].dropna():
    all_tags.update(tags.split(','))

# Write the modified DataFrame back to CSV and TXT files
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

for value in unique_values:
    # Sanitize the string to replace problematic characters
    sanitized_value = value.replace('/', '_')  # Replace '/' with '_'
    csv_output_file = os.path.join(output_dir, f'{sanitized_value}.csv')
    txt_output_file = os.path.join(output_dir, f'{sanitized_value}.txt')
    
    # Filter the DataFrame based on the current value
    filtered_df = df[df['List Name'] == value]
    
    # Drop additional columns from the filtered DataFrame
    additional_columns_to_drop = ['Space Name', 'List Name']  # Replace with the names of columns you want to drop
    filtered_df = filtered_df.drop(columns=additional_columns_to_drop)
    
    # Create a list to hold the final sorted rows
    sorted_rows = []
    
    # Function to add tasks and their children
    def add_task_with_children(task_id):
        task_rows = filtered_df[filtered_df['Task ID'] == task_id].values.tolist()
        for row in task_rows:
            sorted_rows.append(row)
            child_tasks = filtered_df[filtered_df['Parent ID'] == task_id]['Task ID'].unique()
            for child_task in child_tasks:
                add_task_with_children(child_task)
    
    # Find all tasks that do not have a parent (top-level tasks)
    top_level_tasks = filtered_df[filtered_df['Parent ID'].isna()]['Task ID'].unique()
    
    # Add top-level tasks and their children to the sorted rows
    for task_id in top_level_tasks:
        add_task_with_children(task_id)
    
    # Convert the list of sorted rows back to a DataFrame
    sorted_df = pd.DataFrame(sorted_rows, columns=filtered_df.columns)
    
    # Write the sorted DataFrame to a CSV file
    sorted_df.to_csv(csv_output_file, index=False)
    
    # Write the sorted DataFrame to a TXT file without "Task ID" and "Parent ID" columns and removing NaN and []
    txt_columns_to_exclude = ['Task ID', 'Parent ID']
    sorted_df_txt = sorted_df.drop(columns=txt_columns_to_exclude)
    sorted_df_txt = sorted_df_txt.replace(['NaN', '[]'], '')
    
    with open(txt_output_file, 'w', encoding='utf-8') as f:
        for index, row in sorted_df_txt.iterrows():
            cleaned_row = [f"(({value}))" if pd.notna(value) and col == 'Task Content' else str(value) if pd.notna(value) else '' 
                           for col, value in zip(sorted_df_txt.columns, row.values)]
            f.write('\t'.join(cleaned_row) + '\n')
    
    # Write the DataFrame to tag-specific folders
    for tag in all_tags:
        # Escape special characters in the tag
        escaped_tag = re.escape(tag.strip())
        tag_filtered_df = sorted_df[sorted_df['Tags'].str.contains(escaped_tag, na=False)]
        if not tag_filtered_df.empty:
            tag_dir = os.path.join(output_dir, tag.strip())
            os.makedirs(tag_dir, exist_ok=True)
            tag_csv_output_file = os.path.join(tag_dir, f'{sanitized_value}.csv')
            tag_txt_output_file = os.path.join(tag_dir, f'{sanitized_value}.txt')
            
            tag_filtered_df.to_csv(tag_csv_output_file, index=False)
            
            tag_filtered_df_txt = tag_filtered_df.drop(columns=txt_columns_to_exclude)
            tag_filtered_df_txt = tag_filtered_df_txt.replace(['NaN', '[]'], '')
            
            with open(tag_txt_output_file, 'w', encoding='utf-8') as f:
                for index, row in tag_filtered_df_txt.iterrows():
                    cleaned_row = [f"(({value}))" if pd.notna(value) and col == 'Task Content' else str(value) if pd.notna(value) else '' 
                                   for col, value in zip(tag_filtered_df_txt.columns, row.values)]
                    f.write('\t'.join(cleaned_row) + '\n')

print(f'Processed {len(df)} rows and saved them as .csv and .txt files in the "{output_dir}" directory and tag-specific subdirectories.')
