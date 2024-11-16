import csv
from pathlib import Path
from django.core.files import File
from ..models import Product, Category

BASE_DIR = Path(__file__).resolve().parent

def populate():
    category = Category.objects.get(category_name="Muqbis")
    with open(BASE_DIR / "products.csv", encoding="utf8") as f:
        reader = csv.reader(f)
        next(reader, None)
        i = 1
        for row in reader:
            img_location = rf"{BASE_DIR}/imgs/{i}.jpg"
            img_file = File(open(img_location, "rb"))

            product = Product.objects.create(
                product_id=row[0],
                product_name=row[1],
                description_en=row[2],
                description_ar=row[3],
                product_page_link=row[5],
                original_price=row[6].replace("٫", "."),
                discount=row[7],
                price_after_discount=row[8].replace("٫", "."),
                price_points=row[9],
                coupon=row[10],
                category=category,
            )
            product.img.save(name=f"{row[0]}.jpg", content=img_file)
            product.save()
            i += 1