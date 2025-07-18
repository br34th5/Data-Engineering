import os
import pandas as pd
import re
import glob

#TBD: radau neatitikima: sub_task folderiuose esantys txt failai turi ne tik sau priklausanti turini, bet ir tarsi i juos appendintas is  kitu sub_tasku turinys

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
    sanitized = re.sub(r'[<>:"/\\|?*]', '', str(name)).strip()  # Remove invalid chars and leading/trailing whitespace
    sanitized = sanitized.rstrip('.')  # Remove trailing dots for cross-platform compatibility
    sanitized = sanitized.replace('.', '')  # Remove all periods for compatibility
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
    def add_task_with_children(task_id, parent_folder, is_child=False):
        task_rows = filtered_df[filtered_df['Task ID'] == task_id].values.tolist()
        for row in task_rows:
            sorted_rows.append(row)
            task_name = row[filtered_df.columns.get_loc("Task Name")]
            sanitized_task_name = sanitize_name(task_name)  # Sanitize Task Name

            # If it's a child task, create a subfolder; if it's top-level, use the parent_folder directly
            if is_child:
                subtask_folder = os.path.join(parent_folder, sanitized_task_name)
                os.makedirs(subtask_folder, exist_ok=True)
                target_folder = subtask_folder
            else:
                target_folder = parent_folder
            
            # Collect children of the current task
            child_tasks = filtered_df[filtered_df['Parent ID'] == task_id]['Task ID'].unique()
            for child_task in child_tasks:
                add_task_with_children(child_task, target_folder, is_child=True)
            
            # Create and write to the text file inside the target folder
            sorted_df = pd.DataFrame(sorted_rows, columns=filtered_df.columns)
            txt_output_file = os.path.join(target_folder, f'{sanitized_task_name}.txt')
            
            # Exclude specific columns and clean the content
            txt_columns_to_exclude = ['Task ID', 'Parent ID']
            sorted_df_txt = sorted_df.drop(columns=txt_columns_to_exclude)
            sorted_df_txt = sorted_df_txt.replace(['NaN', '[]'], '')
            sorted_df_txt = sorted_df_txt.apply(
                lambda col: col.map(lambda x: re.sub(r'\n+', ' ', str(x)) if pd.notna(x) else x)
            )

            with open(txt_output_file, 'w', encoding='utf-8') as f:
                for _, row in sorted_df_txt.iterrows():
                    cleaned_row = [f"(({val}))" if pd.notna(val) and col == 'Task Content' else str(val) if pd.notna(val) else '' 
                                   for col, val in zip(sorted_df_txt.columns, row.values)]
                    f.write('\t'.join(cleaned_row) + '\n')
                    # Separator lines for clarity
                    f.write("                                                          \n")  # Add separator line for clarity

    # Find top-level tasks (no parent) and create folders for each
    top_level_tasks = filtered_df[filtered_df['Parent ID'].isna()]
    for _, task_row in top_level_tasks.iterrows():
        task_id = task_row['Task ID']
        task_name = task_row['Task Name']
        
        # Sanitize and create folder for the top-level task
        sanitized_task_name = sanitize_name(task_name)
        task_folder = os.path.join(list_folder, sanitized_task_name)
        os.makedirs(task_folder, exist_ok=True)

        # Add tasks with the new folder structure
        sorted_rows.clear()
        add_task_with_children(task_id, task_folder)

print(f'Processed {len(df)} rows and saved them in the "{output_dir}" directory with the specified folder structure.')

