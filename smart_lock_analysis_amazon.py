import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('smart_locks_data1.csv')

# a. Number of brands in the segment
num_brands = df['Brand name'].nunique()
print(f"Number of brands in the segment: {num_brands}")

# b. Count of SKUs per brand
sku_count = df['Brand name'].value_counts()
print("\nCount of SKUs per brand:")
print(sku_count)

# c. Relative ranking
def calculate_relative_ranking(group):
    return group['Ranking'].mean()

relative_ranking = df.groupby('Brand name').apply(calculate_relative_ranking).sort_values()
print("\nRelative ranking of brands:")
print(relative_ranking)

# d. Relative rating
def calculate_relative_rating(group):
    return group['Rating'].mean()

relative_rating = df.groupby('Brand name').apply(calculate_relative_rating).sort_values(ascending=False)
print("\nRelative rating of brands:")
print(relative_rating)

# e. Price distribution of SKUs
def categorize_price(price):
    if price < 3000:
        return '<INR 3000'
    elif 3000 <= price < 5000:
        return 'INR 3000-4999'
    elif 5000 <= price < 10000:
        return 'INR 5000-9999'
    elif 10000 <= price < 15000:
        return 'INR 10000-14999'
    elif 15000 <= price < 20000:
        return 'INR 15000-19999'
    else:
        return 'Greater than 20000'

df['Price Band'] = df['Price'].apply(categorize_price)
price_distribution = df['Price Band'].value_counts().sort_index()
print("\nPrice distribution of SKUs:")
print(price_distribution)

# Visualizations for the presentation
plt.figure(figsize=(12, 6))
sku_count.plot(kind='bar')
plt.title('Count of SKUs per Brand')
plt.xlabel('Brand')
plt.ylabel('Number of SKUs')
plt.tight_layout()
plt.savefig('sku_count.png')

plt.figure(figsize=(12, 6))
relative_ranking.plot(kind='bar')
plt.title('Relative Ranking of Brands')
plt.xlabel('Brand')
plt.ylabel('Average Ranking')
plt.tight_layout()
plt.savefig('relative_ranking.png')

plt.figure(figsize=(12, 6))
relative_rating.plot(kind='bar')
plt.title('Relative Rating of Brands')
plt.xlabel('Brand')
plt.ylabel('Average Rating')
plt.tight_layout()
plt.savefig('relative_rating.png')

plt.figure(figsize=(12, 6))
price_distribution.plot(kind='bar')
plt.title('Price Distribution of SKUs')
plt.xlabel('Price Band')
plt.ylabel('Number of SKUs')
plt.tight_layout()
plt.savefig('price_distribution.png')

print("Analysis complete. Visualizations saved as PNG files.")

# from pptx import Presentation
# from pptx.util import Inches

# # Create a PowerPoint presentation
# prs = Presentation()

# # Title Slide
# slide_layout = prs.slide_layouts[0]
# slide = prs.slides.add_slide(slide_layout)
# title = slide.shapes.title
# subtitle = slide.placeholders[1]
# title.text = "Smart Lock Market Analysis"
# subtitle.text = "Data Scraping and Analysis Report"

# # Slide 1: Top Brands by SKU Count
# slide_layout = prs.slide_layouts[5]
# slide = prs.slides.add_slide(slide_layout)
# title = slide.shapes.title
# title.text = "Top Brands by SKU Count"

# img_path = 'sku_count.png'
# left = Inches(1)
# top = Inches(1.5)
# height = Inches(4.5)
# pic = slide.shapes.add_picture(img_path, left, top, height=height)

# # Slide 2: Top Brands by Average Rating
# slide_layout = prs.slide_layouts[5]
# slide = prs.slides.add_slide(slide_layout)
# title = slide.shapes.title
# title.text = "Top Brands by Average Rating"

# img_path = 'relative_rating.png'
# left = Inches(1)
# top = Inches(1.5)
# height = Inches(4.5)
# pic = slide.shapes.add_picture(img_path, left, top, height=height)

# # Slide 3: Data Summary
# slide_layout = prs.slide_layouts[1]
# slide = prs.slides.add_slide(slide_layout)
# title = slide.shapes.title
# title.text = "Data Summary"
# content = slide.placeholders[1]
# content.text = f"Total Brands: {df['Brand name'].nunique()}\nTotal Products: {len(df)}\n\nTop Brands by SKU Count:\n{sku_count.to_string(index=False)}\n\nTop Brands by Average Rating:\n{relative_rating.to_string(index=False)}"

# # Save the PowerPoint presentation
# prs.save('smart_lock_market_analysis.pptx')
