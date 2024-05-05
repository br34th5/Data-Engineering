import os
import pandas as pd

#preparing clickup exported CSV file for cleaning unnecessary columns
# Read the CSV file into a DataFrame
csv_file = 'export_copy.csv'  # Replace 'your_file.csv' with the path to your CSV file
df = pd.read_csv(csv_file)

# Specify the columns you want to delete
columns_to_delete = ['Task ID', 'Attachments', 'Date Created', 'Date Created Text','Due Date', 'Due Date Text','Start Date', 'Start Date Text','Assignees', 'Folder Name', 'Time Estimated', 
                     'Time Estimated Text', 'Checklists', 'Comments', 'Assigned Comments', 'Time Spent', 'Time Spent', 'Time Spent Text',
                      'Rolled Up Time', 'Rolled Up Time Text']  
# Replace with the names of columns you want to delete

# Drop the specified columns from the DataFrame
df = df.drop(columns=columns_to_delete)

# Sort the DataFrame by the "Space Name" column
df_sorted = df.sort_values(by='Space Name')

# Get all the unique values in the "List Name" column
unique_values = df_sorted['List Name'].unique()
# Print or use the unique values as needed
print(unique_values)

# Write the modified DataFrame back to a CSV file
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)
for value in unique_values:
    # Sanitize the string to replace problematic characters
    sanitized_value = value.replace('/', '_')  # Replace '/' with '_'
    output_file = os.path.join(output_dir, f'{sanitized_value}.csv')
    # Filter the DataFrame based on the current value
    filtered_df = df[df['List Name'] == value]
    # Drop additional columns from the filtered DataFrame
    additional_columns_to_drop = ['Space Name', 'List Name']  # Replace with the names of columns you want to drop
    filtered_df = filtered_df.drop(columns=additional_columns_to_drop)
    # Write the filtered DataFrame to a CSV file
    filtered_df.to_csv(output_file, index=False)
