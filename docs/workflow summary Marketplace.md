# workflow summary Marketplace APP


---

## **1. Product Browsing and Search**

### **Model**:

```python
class Product(models.Model):
    name_en, name_ar
    description_en, description_ar
    price, discount
    brand, category
```

### **API**:

**GET /products/**
Returns a paginated list of products.

### **Filters** (via DjangoFilter + SearchFilter):

* `brand__slug`
* `category__slug`
* `price` (min/max)
* `search=name_en,name_ar,brand__slug`

### **Example Request**:

```http
GET /products/?search=cream&brand__slug=curlit&category__slug=hair
```

### **Example Response**:

```json
{
  "id": 1,
  "name_en": "Leave-In Conditioner",
  "price": 200,
  "discount": 10,
  "discounted_price": 180,
  "is_wishlisted": true,
  "brand": "curlit",
  "category": "hair"
}
```

---

## **2. Wishlist Management**

### **API**:

* `GET /wishlist/` → Get user’s wishlist
* `POST /wishlist/<product_id>/` → Add product
* `DELETE /wishlist/<product_id>/` → Remove product

### **Example Response** (GET):

```json
{
  "id": 1,
  "products": [
    {
      "id": 2,
      "name_en": "Hair Gel",
      "is_wishlisted": true
    }
  ]
}
```

---

## **3. Brand & Category**

### **GET /brands/**

Returns all brands
Supports: `search=name`

### **GET /categories/**

Returns all categories
Supports: `search=name`

---

## **4. Cart Management**

### **Model Design**:

```python
Cart → user, brand  
CartItem → cart, product, quantity
```

### **API**:

* `GET /cart/items/` → List items
* `POST /cart/items/` → Add/update item
* `PATCH /cart/items/<id>/` → Update quantity
* `DELETE /cart/items/<id>/` → Remove item

### **Request Body (POST)**:

```json
{
  "product": 1,
  "quantity": 2
}
```

### **Business Rules**:

* Cart must contain only one brand at a time
* Cart auto-assigns brand on first item
* If item removed and cart becomes empty → brand reset to null

---

## **5. Cart Summary / Checkout Eligibility**

### **GET /cart/**

Returns full cart with pricing + tier logic + checkout eligibility

### **Cart Summary Includes**:

* `total_price` → Sum of item prices
* `tier_discount` → Based on user's brand points
* `discounted_total_price` → total - discount
* `points` → User's total points
* `current_tier` → Best matched tier (if exists)
* `can_checkout` → True only if tier exists

### **Example Response**:

```json
{
  "brand": "curlit",
  "total_price": 300,
  "tier_discount": 10,
  "discounted_total_price": 270,
  "points": 270,
  "current_tier": {
    "discount": 10,
    "required_points": 200
  },
  "can_checkout": true
}
```

---

## **6. Tier & Brand Points System**

### **Model Logic**:

* `Tier`: brand → list of `{points_required, discount_percent}`
* `UserBrandPoints`: user → brand → points

### **GET /tiers/**

Returns grouped list of all tiers by brand

### **GET /tiers/\<brand\_slug>/**

Returns tier list for specific brand

---

## **7. Request/Response Body Cheatsheet**

| Endpoint                 | Method | Request Body                | Notes                                                                                                                                                                |
|--------------------------|--------| --------------------------- |----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/products/`             | GET    | None                        | Filters: brand, category & search basend on name_ar , name_en , brand_slug  , also if added in header access token will get product list marked if wishlisted or not |
| `/brands/`               | GET    | None                        | get all brands name & slug                                                                                                                                           |
| `/categories/`             | GET    | None                        | get all categories name & slug                                                                                                                                       |
| `/wishlist/{{product_id}}/` | POST   | None                        | add or remove product from wishlist                                                                                                                                  |
| `/wishlist/` | get    | None                        | get specific user wishlist                                                                                                                                           |
| `/cart/items/`           | POST   | `{product: 1, quantity: 2}` | Adds to cart                                                                                                                                                         |
| `/cart/items/{{item_id}}/` | PATCH  | `{quantity: 3}`             | Update qty                                                                                                                                                           |
| `/cart/items/{{item_id}}/` | DELETE | None                        | Removes item                                                                                                                                                         |
| `/cart/`                 | GET    | None                        | Returns full cart summary                                                                                                                                            |
| `/tiers/`                | GET    | None                        | Grouped by brand                                                                                                                                                     |
| `/tiers/{{brand_slug}}/` | GET    | None                        | Tiers for brand                                                                                                                                                      |

---

## 🔁 **System Workflow Diagram**

---

```
[User - Frontend]
     |
     | 1. Load Product List
     v
[GET /products/?search=cream&brand__slug=curlit]
     |
     |---> [ProductViewSet]
     |        ↳ Filters by name, brand, category
     |        ↳ Adds is_wishlisted if authenticated
     |        ↳ Returns paginated list with discounted price
     |
     v
[Product List Screen]

     |
     | 2. View Product Details
     v
[GET /products/<id>/]
     |
     |---> [ProductViewSet.retrieve]
     |        ↳ Returns full product details + discounted price
     |
     v
[Product Detail Screen]

     |
     | 3. Add to Cart
     v
[POST /cart/items/]
Body:
{
  "product": 1,
  "quantity": 2
}
     |
     |---> [CartItemAPIView.post()]
     |        ↳ Checks brand match or assigns brand to cart
     |        ↳ Adds item or updates quantity
     |
     v
[Cart updated]

     |
     | 4. View Cart Items (Optional)
     v
[GET /cart/items/]
     |
     |---> [CartItemAPIView.get()]
     |        ↳ Returns all cart items with quantity & price
     |
     v
[Mini Cart Display]

     |
     | 5. View Full Cart Summary
     v
[GET /cart/]
     |
     |---> [CartSummaryAPIView.get()]
     |        ↳ Calculates:
     |             - total_price
     |             - user total_points
     |             - user brand_points
     |             - matching tier (if any)
     |             - discount percent
     |             - final_price = total - discount
     |             - can_checkout (True if valid tier)
     |
     v
[Cart Summary Screen]

     |
     | 6. Backend Response:
     v
{
  "total_price": 400,
  "tier_discount": 10,
  "discounted_total_price": 360,
  "points": 270,
  "current_tier": {
    "discount": 10,
    "required_points": 200
  },
  "can_checkout": true
}

     |
     | 7. Frontend checks `can_checkout`:
     |       - if True => Enable checkout button (green)
     |       - else => Disable checkout
     |
     v
[Checkout Button UI State]

     |
     | 8. Final Step (not yet implemented):
     v
[POST /checkout/]
     |
     |---> (To Be Developed)
     |        ↳ Deduct points
     |        ↳ get copoun
     |        ↳ Clear cart
     |
     v
[Success screen + order summary]
```

---

## ✅ Summary of Workflow Steps:

1. Product list filtered & searchable
2. Product detail view with discount logic
3. Add to cart with brand validation
4. Cart items overview
5. Cart summary:

  * Full pricing
  * Points
  * Tier match
  * Discount
  * Checkout logic
6. Tier-based discount logic applied dynamically
7. User only allowed to checkout if `can_checkout = true`


