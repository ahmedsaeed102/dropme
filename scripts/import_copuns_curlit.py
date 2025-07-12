import os
import sys
import django
import pandas as pd

# Step 1: Setup Django project
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # Change if needed
django.setup()

# Step 2: Import models
from marketplace.models import Coupon, Brand  # Adjust app name if different

# Step 3: Load Excel file
file_path = os.path.join(SCRIPT_DIR, 'Curlit_static_coupon.xlsx')
df = pd.read_excel(file_path)

# Step 4:  columns
df.columns = df.columns.str.strip()  # Remove leading/trailing spaces

column_mapping = {
    'Code': 'code',
    'Discount': 'discount',
    'Tier Points': 'points_required',
    'Type': 'type',
    'Status': 'status'
}
df.rename(columns=column_mapping, inplace=True)

# Step 5: Validate required columns
required_columns = ['code', 'discount', 'points_required', 'type', 'status']
for col in required_columns:
    if col not in df.columns:
        raise Exception(f"Missing column: {col}")

# Step 6: Get curlit brand
try:
    brand = Brand.objects.get(slug='curlit')
except Brand.DoesNotExist:
    raise Exception("Brand 'curlit' not found in the database")

# Step 7: Insert/update coupons
created = 0
updated = 0
skipped = 0

for _, row in df.iterrows():
    try:
        code = str(row['code']).strip()
        discount = int(row['discount'])
        points_required = int(row['points_required'])
        type_ = str(row['type']).lower()
        status = str(row['status']).lower()

        if not all([code, type_, status]):
            skipped += 1
            continue

        coupon, created_flag = Coupon.objects.get_or_create(
            code=code,
            defaults={
                'brand': brand,
                'discount': discount,
                'points_required': points_required,
                'type': type_,
                'status': status
            }
        )

        if not created_flag:
            coupon.discount = discount
            coupon.points_required = points_required
            coupon.type = type_
            coupon.status = status
            coupon.brand = brand
            coupon.save()
            updated += 1
        else:
            created += 1
    except Exception as e:
        print(f"Error with row: {row.to_dict()} — {e}")
        skipped += 1

# Step 8: Summary
print(f"✅ {created} coupons created")
print(f"🔁 {updated} coupons updated")
print(f"⚠️ {skipped} rows skipped due to missing/invalid data")
