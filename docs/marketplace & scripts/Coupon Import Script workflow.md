# 🧾 Coupon Import Script Documentation

This script allows you to **bulk import and update coupons** into your Django app from an Excel file (`.xlsx`). It's designed specifically for brands like **Curlit**, and works with a defined Excel structure.

---

### 📁 File Structure

Place the following files in the same directory:

```
project_root/
│
├── manage.py
├── core/
│   └── settings.py
├── marketplace/
│   └── models.py
│
├── scripts/
│   ├── load_coupons.py         ← The import script
│   └── Curlit_static_coupon.xlsx  ← The Excel file
```

---

### 📋 Excel Format Required

Your Excel file **must contain these exact columns** (with proper capitalization and no spaces at the start or end):

| Code   | Discount | Tier Points | Type    | Status |
| ------ | -------- | ----------- | ------- | ------ |
| ABC123 | 10       | 100         | online  | unused |
| XYZ456 | 15       | 200         | offline | used   |

* **Code**: Unique string for the coupon.
* **Discount**: Percentage (e.g., 10).
* **Tier Points**: Required user points to unlock coupon.
* **Type**: `online` or `offline`.
* **Status**: `used` or `unused`.

---

### ⚙️ Setup & Usage

1. **Navigate to your project root**
   In terminal:

   ```bash
   cd scripts
   ```

2. **Run the script**:

   ```bash
   python import_copuns_curlit.py
   ```

---

### 🔍 What the Script Does

1. Loads the Excel file.
2. Cleans and maps columns to match the `Coupon` model fields.
3. Verifies if the brand `curlit`  `brand = Brand.objects.get(slug='curlit')` or other you can change it exists.
4. For each row:

    * If a coupon with that code exists → it updates the record.
    * If not → it creates a new coupon with the given values.

---

### ✅ Output Example

```bash
✅ 8 coupons created
🔁 3 coupons updated
⚠️ 1 rows skipped due to missing/invalid data
```
---
#### all rights back to Bassanthossamxx
