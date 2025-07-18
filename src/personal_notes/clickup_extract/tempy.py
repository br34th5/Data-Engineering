import os
import pandas as pd
import re

# Specify the CSV file path
csv_file = 'clickup10-25.csv'  # Replace with the path to your CSV file
df = pd.read_csv(csv_file)

# Strip whitespace from column names immediately after loading
df.columns = df.columns.str.strip()

# Columns to delete (excluding "Task ID" and "Parent ID")
columns_to_delete = ['Attachments', 'Date Created', 'Date Created Text', 'Due Date', 'Due Date Text',
                     'Start Date', 'Start Date Text', 'Assignees', 'Folder Name', 'Time Estimated',
                     'Time Estimated Text', 'Checklists', 'Comments', 'Assigned Comments', 'Time Spent',
                     'Time Spent Text', 'Rolled Up Time', 'Rolled Up Time Text', 'Priority', 'Status']

# Drop specified columns
df = df.drop(columns=columns_to_delete)

# Sort the DataFrame by the "Space Name" column
df_sorted = df.sort_values(by='Space Name')

# Get unique values in the "List Name" column
unique_values = df_sorted['List Name'].unique()

# Define output directory
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# Define a maximum length for folder and file names (adjust as needed)
MAX_NAME_LENGTH = 100

# Utility function to sanitize names
def sanitize_name(name):
    # Remove invalid characters and truncate
    sanitized = re.sub(r'[<>:"/\\|?*]', '', str(name))
    return sanitized[:MAX_NAME_LENGTH]  # Truncate if necessary

# Process each unique List Name
for value in unique_values:
    sanitized_list_name = sanitize_name(value)  # Sanitize List Name
    list_folder = os.path.join(output_dir, sanitized_list_name)
    os.makedirs(list_folder, exist_ok=True)
    
    # Filter DataFrame based on the current List Name value
    filtered_df = df[df['List Name'] == value]
    
    # Drop columns 'Space Name' and 'List Name'
    filtered_df = filtered_df.drop(columns=['Space Name', 'List Name'])
    
    # Prepare a list to hold sorted rows
    sorted_rows = []
    
    # Define function to add tasks and their children
    def add_task_with_children(task_id):
        task_rows = filtered_df[filtered_df['Task ID'] == task_id].values.tolist()
        for row in task_rows:
            sorted_rows.append(row)
            child_tasks = filtered_df[filtered_df['Parent ID'] == task_id]['Task ID'].unique()
            for child_task in child_tasks:
                add_task_with_children(child_task)
    
    # Find top-level tasks (no parent) and create folders for each
    top_level_tasks = filtered_df[filtered_df['Parent ID'].isna()]

    for _, task_row in top_level_tasks.iterrows():
        task_id = task_row['Task ID']
        task_name = task_row['Task Name']
        
        # Sanitize the task name for folder and file naming
        sanitized_task_name = sanitize_name(task_name)  # Sanitize Task Name

        # Create folder for the top-level task using the sanitized name
        task_folder = os.path.join(list_folder, sanitized_task_name)
        os.makedirs(task_folder, exist_ok=True)

        # Collect children of the top-level task
        sorted_rows.clear()
        add_task_with_children(task_id)
        
        # Convert to DataFrame
        sorted_df = pd.DataFrame(sorted_rows, columns=filtered_df.columns)

        # Name the text file based on the parent task's name
        txt_output_file = os.path.join(task_folder, f'{sanitized_task_name}.txt')
        
        # Check for filename length and truncate if necessary
        if len(txt_output_file) > 255:
            txt_output_file = os.path.join(task_folder, f'{sanitized_task_name[:255]}.txt')
        
        txt_columns_to_exclude = ['Task ID', 'Parent ID']
        sorted_df_txt = sorted_df.drop(columns=txt_columns_to_exclude)
        sorted_df_txt = sorted_df_txt.replace(['NaN', '[]'], '')
        
        # Write to the text file
        with open(txt_output_file, 'w', encoding='utf-8') as f:
            for _, row in sorted_df_txt.iterrows():
                cleaned_row = [f"(({val}))" if pd.notna(val) and col == 'Task Content' else str(val) if pd.notna(val) else '' 
                               for col, val in zip(sorted_df_txt.columns, row.values)]
                f.write('\t'.join(cleaned_row) + '\n')
                f.write("----------------------------------------------------\n")  # Add separator line after each child's content

print(f'Processed {len(df)} rows and saved them in the "{output_dir}" directory with the specified folder structure.')
