import pandas as pd
import matplotlib.pyplot as plt

# Load the Totals sheet
file_path = '/home/eikov/fin/analysis/Manually-polished/2025/Galutinis_spendings.xlsx'  # change filename
df = pd.read_excel(file_path, sheet_name='Totals')

# Ensure SUMA is numeric (clean up bad values)
df['SUMA'] = pd.to_numeric(df['SUMA'], errors='coerce')  # convert non-numeric to NaN
df = df.dropna(subset=['SUMA'])  # drop rows where SUMA couldn't be converted

# Group by Category (or Subcategory)
grouped = df.groupby('Category')['SUMA'].sum().sort_values(ascending=False)

# Optional: filter out zero or very small values
grouped = grouped[grouped > 0]

# Plot
plt.figure(figsize=(8, 8))
grouped.plot.pie(autopct='%1.1f%%', startangle=90)
plt.title('Spending Distribution by Category')
plt.ylabel('')
plt.tight_layout()

# Save pie chart
output_path = '/home/eikov/fin/analysis/spending_pie_by_category.png'
plt.savefig(output_path)
print(f"Saved pie chart to: {output_path}")
