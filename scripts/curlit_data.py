import os
import sys
import django
import pandas as pd

# Step 1: Setup Django project
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Step 2: Import models
from marketplace.models import Product, Brand, Category

# Step 3: Load Excel file
file_path = os.path.join(SCRIPT_DIR, 'curlit_product_list.xlsx')
df = pd.read_excel(file_path)

# Step 4: Check required columns
required_columns = [
    'name_en', 'name_ar', 'description_en', 'description_ar',
    'image_url', 'product_page_link', 'price', 'discount'
]
for col in required_columns:
    if col not in df.columns:
        raise Exception(f"Missing column: {col}")

# Step 5: Get brand and category
brand = Brand.objects.get(slug='curlit')
category = Category.objects.get(slug='cosmetics')

# Step 6: Create or update products
created = 0
updated = 0
for _, row in df.iterrows():
    # Split the image_url column by commas
    image_urls = [url.strip() for url in str(row['image_url']).split(',') if url.strip()]

    product, created_flag = Product.objects.get_or_create(
        name_en=row['name_en'],
        defaults={
            'name_ar': row['name_ar'],
            'description_en': row['description_en'],
            'description_ar': row['description_ar'],
            'img_urls': image_urls,
            'product_page_link': row['product_page_link'],
            'price': row['price'],
            'discount': row['discount'],
            'brand': brand,
            'category': category,
        }
    )

    if not created_flag:
        # Update existing product with new data
        product.name_ar = row['name_ar']
        product.description_en = row['description_en']
        product.description_ar = row['description_ar']
        product.img_urls = image_urls
        product.product_page_link = row['product_page_link']
        product.price = row['price']
        product.discount = row['discount']
        product.brand = brand
        product.category = category
        product.save()
        updated += 1
    else:
        created += 1

print(f"{created} products created, {updated} products updated.")
