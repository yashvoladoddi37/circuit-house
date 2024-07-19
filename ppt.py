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
# content.text = f"Total Brands: {df['Brand name'].nunique()}\nTotal Products: {len(df)}\n\nTop Brands by SKU Count:\n{top_brands.to_string(index=False)}\n\nTop Brands by Average Rating:\n{avg_rating.to_string(index=False)}"

# # Save the PowerPoint presentation
# prs.save('smart_lock_market_analysis.pptx')
