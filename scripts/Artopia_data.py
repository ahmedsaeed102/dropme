import os
import sys
import django
import pandas as pd

# Step 1: Django Setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Step 2: Import models
from marketplace.models import Product, Brand, Category

#  Step 3: Load Excel file
file_path = os.path.join(SCRIPT_DIR, 'Artopia_translated_products.xlsx')
df = pd.read_excel(file_path)

#  Step 4: Columns check
required_columns = [
    'name_ar', 'name_en', 'original_price', 'discount',
    'description_ar', 'description_en', 'image_url',
    'product_url', 'category'
]
for col in required_columns:
    if col not in df.columns:
        raise Exception(f"Missing column: {col}")

#  Step 5: Prepare brand
brand = Brand.objects.get(slug='artopia')

#  Step 6: Loop and import
created, updated = 0, 0
for _, row in df.iterrows():
    # Skip if essential data is missing
    if pd.isna(row['name_en']) or pd.isna(row['original_price']):
        continue

    # Category by slugified name
    category_slug = str(row['category']).strip().lower().replace(' ', '-')
    try:
        category = Category.objects.get(slug=category_slug)
    except Category.DoesNotExist:
        # Create the category if not found
        category = Category.objects.create(
            name=row['category'].strip(),
            slug=category_slug
        )
        print(f"✅ Created new category: {row['category'].strip()} with slug: {category_slug}")

    # Multiple image handling
    image_urls = [url.strip() for url in str(row['image_url']).split(',') if url.strip()]

    # Create or update product
    product, created_flag = Product.objects.get_or_create(
        name_en=row['name_en'].strip(),
        defaults={
            'name_ar': row['name_ar'],
            'description_en': row['description_en'],
            'description_ar': row['description_ar'],
            'img_urls': image_urls,
            'product_page_link': row['product_url'],
            'price': float(row['original_price']),
            'discount': float(row['discount']) if not pd.isna(row['discount']) else 0,
            'brand': brand,
            'category': category,
        }
    )

    if not created_flag:
        # Update existing
        product.name_ar = row['name_ar']
        product.description_en = row['description_en']
        product.description_ar = row['description_ar']
        product.img_urls = image_urls
        product.product_page_link = row['product_url']
        product.price = float(row['original_price'])
        product.discount = float(row['discount']) if not pd.isna(row['discount']) else 0
        product.brand = brand
        product.category = category
        product.save()
        updated += 1
    else:
        created += 1

print(f"{created} products created, {updated} products updated.")
