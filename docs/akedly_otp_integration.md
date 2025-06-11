
# 🔐 Akedly OTP Integration – DropMe Auth Refactor

## ✨ Overview

This document describes the refactor made to the authentication system in order to integrate [Akedly.io](https://akedly.io), a transaction-based OTP service. The goal of this refactor is to offload OTP generation, delivery, and verification to Akedly’s secure infrastructure, improving delivery reliability, security, and code maintainability.

---

## ✅ Key Changes

### 🔄 Replaced:
- Manual OTP generation (`random.randint`, local `otp` field)
- Manual expiration and retry handling
- Local verification logic using `otp_expiration`, `max_otp_try`, etc.

### ✅ Added:
- Integration with **Akedly's 3-step OTP API flow**
- Akedly transaction tracking via:
  - `akedly_transaction_id`
  - `akedly_request_id`

---

## 🔧 Akedly OTP Flow

1. **Create OTP Transaction**  
   Call: `POST /api/v1/transactions`  
   ➜ Gets a `transactionID`

2. **Activate Transaction**  
   Call: `POST /api/v1/transactions/activate/{transactionID}`  
   ➜ Sends OTP via multiple channels (email, WhatsApp, SMS)

3. **Verify OTP**  
   Call: `POST /api/v1/transactions/verify/{_id}`  
   ➜ Returns success/failure + metadata

---

## 🧱 Model Changes

### `UserModel`

```python
akedly_transaction_id = models.CharField(max_length=255, null=True, blank=True)
akedly_request_id = models.CharField(max_length=255, null=True, blank=True)
```

- These fields replace the need for `otp`, `otp_expiration`, etc.
- Both are updated during user creation.

---

## 📩 Updated OTP Logic

### `UserSerializer.create()`

- After creating the user, we:
  1. Call Akedly to start a transaction
  2. Activate the transaction to send the OTP
  3. Save both `transaction_id` and `_id` in the user model

```python
from utils.akedly import create_otp_transaction, activate_otp_transaction

transaction_id = create_otp_transaction(user.email, full_phone)
request_id = activate_otp_transaction(transaction_id)
```

If any step fails, the user is deleted and an error is returned.

---

### `verify_otp()` View

- Accepts the user’s OTP input
- Sends it to Akedly’s verification API
- If valid, activates the user, deletes the Akedly IDs, and rewards recycled points (if phone matched)

```python
if akedly_verify_otp(instance.akedly_request_id, otp):
    instance.is_active = True
```

---

## 🔁 Regenerating OTP

You can allow OTP resends by:
- Calling the same `create_otp_transaction()` + `activate_otp_transaction()` again
- Updating the `akedly_transaction_id` and `akedly_request_id`

---

## 🧪 Testing

**Signup Flow**
- Should trigger OTP via email/SMS
- User should receive OTP and enter it
- Successful verification should mark them `is_active=True`

**Failure Cases**
- Invalid OTP → 403 with error
- API error from Akedly → handled with validation message

---

## 🧾 Migration Notes

If you face errors like:
```bash
django.db.utils.ProgrammingError: relation "users_api_usermodel" does not exist
```

Do this:
1. Ensure `AUTH_USER_MODEL` is set to `users_api.UserModel`
2. Run migrations in order:
```bash
python manage.py migrate users_api
python manage.py migrate
```

If PostGIS is used (for `PointField`s), enable it in Neon:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

---

## 🧑‍💻 Files Affected

| File | Summary |
|------|---------|
| `users/models.py` | Added Akedly fields |
| `users/serializers.py` | Replaced OTP logic in `create()` |
| `users/views.py` | Refactored `verify_otp()` to call Akedly |
| `utils/akedly.py` | Added HTTP clients for Akedly API |
| `settings.py` | Ensured `AUTH_USER_MODEL` is correctly set |

---

## 📝 Commit Message Example

```txt
refactor(auth): integrate Akedly OTP verification into user registration and verification flows

- Replaced internal OTP generation with Akedly's transaction-based OTP API
- Added `akedly_transaction_id` and `akedly_request_id` to `UserModel`
- Updated `UserSerializer.create()` to send and activate OTP via Akedly
- Refactored `verify_otp` view to use Akedly's verify endpoint
- Cleaned unused OTP fields and ensured migration order
```

---

## 🔚 Summary

This refactor externalizes OTP handling to Akedly, simplifying backend logic, improving UX with multi-channel OTP delivery, and reducing the security and performance overhead of managing it in-house.
