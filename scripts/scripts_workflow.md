# Product Import Scripts Guide for Stakeholders

This document outlines how to use our data import scripts to push product entries into the database from Excel files. Each script is designed to work with a specific brand and expects the data in a predefined structure.

---

## 1. `curlit_data.py` — Importing Curlit Products

### ✅ Prerequisites:

* Place the `curlit_product_list.xlsx` file in the **same directory** as the script.
* Ensure all required columns are present and match the script's expectations.

### 📝 Expected Fields:

```python
'name_ar': row['name_ar']
'description_en': row['description_en']
'description_ar': row['description_ar']
'img_urls': image_urls
'product_page_link': row['product_page_link']
'price': row['price']
'discount': row['discount']
'brand': brand
'category': category
```

> **Note:** If there are multiple image URLs, separate them using commas in the `image_url` cell. They will be saved as a list automatically.

### 🔁 Category and Brand:

* Brand slug is hardcoded as `curlit`.
* Category must be passed as a valid **slug**. Refer to the provided category slug list and ensure matching.

### 🚀 How to Run:

```bash
cd scripts
python curlit_data.py
```

### ✅ Success Message:

```text
{created} products created, {updated} products updated.
```

### 🔍 Preview:

Visit: [http://127.0.0.1:8000/marketplace/products/](http://127.0.0.1:8000/marketplace/products/)

---

## 2. `artopia_data.py` — Importing Artopia Products

### ✅ Prerequisites:

* Place the `Artopia_translated_products.xlsx` file in the **same directory** as the script.
* Validate that all columns match the expected field names.
* Ensure category slugs align with your system.

### 📝 Expected Fields:

```python
'name_ar': row['name_ar']
'description_en': row['description_en']
'description_ar': row['description_ar']
'img_urls': image_urls
'product_page_link': row['product_url']
'price': float(row['original_price'])
'discount': float(row['discount']) if not pd.isna(row['discount']) else 0
'brand': brand
'category': category
```

> **Note:** Brand slug is hardcoded as `artopia`. Ensure the file columns match exactly and slugs are correct.

### 🚀 How to Run:

```bash
cd scripts
python artopia_data.py
```

### ✅ Success Message:

```text
{created} products created, {updated} products updated.
```

---
### 🔍 Preview:

Visit: [http://127.0.0.1:8000/marketplace/products/](http://127.0.0.1:8000/marketplace/products/)

---

##  Adding a New Brand

If you want to import data for a new brand:

1. Duplicate one of the existing scripts.
2. Update the brand slug.
3. Match the column names and file name.

> ⚠️ **Reminder:** Once all data is successfully imported and verified, please remove all Excel files before deployment to maintain clean and secure storage.

---

For any issues or updates, contact the backend team.
