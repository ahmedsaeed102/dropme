import requests
#post categories in same request
names = [
    "Accessories", "Art", "Baby Stuff", "Bags", "Cloth", "Dolls",
    "General stuff", "Home Décor", "Keychain", "Kitchen stuff", "Lamps", "Roses", "Cosmetics"
]

for name in names:
    res = requests.post("http://localhost:8000/marketplace/categories/", json={"name": name})
    print(res.status_code, name, res.json())
