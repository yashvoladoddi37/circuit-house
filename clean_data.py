import pandas as pd

# Load the CSV file
df = pd.read_csv('smart_locks_data.csv')

# Extract the brand name as the first word from the 'Brand name' column
df['Brand name'] = df['Brand name'].str.split().str[0]

# Calculate the SKU (number of variations) for each brand
sku_count = df['Brand name'].value_counts().reset_index()
sku_count.columns = ['Brand name', 'SKU']

# Merge the SKU count back into the original DataFrame
df = df.merge(sku_count, on='Brand name', how='left')

# Save the cleaned data to a new CSV file
df.to_csv('smart_locks_data1.csv', index=False)

print(df)
