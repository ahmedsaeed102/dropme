import requests
from PIL import Image
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "products.csv", encoding="utf8") as f:
    reader = csv.reader(f)
    next(reader, None)
    i = 1
    for row in reader:
        image_url = row[4]
        img_data = requests.get(image_url).content
        image_path = BASE_DIR / f"imgs/temp_{i}.jpg"

        with open(image_path, 'wb') as handler:
            handler.write(img_data)

        thumbnail_path = BASE_DIR / f"imgs/{i}.jpg"
        with Image.open(image_path) as img:
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(thumbnail_path, format="JPEG", quality=50, optimize=True)

        image_path.unlink()
        i += 1
