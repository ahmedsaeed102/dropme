import requests

with open("links.txt", 'r') as f:
    i = 0
    for line in f:
        image_url = line

        img_data = requests.get(image_url.strip()).content

        with open(f'{8+i}.jpg', 'wb') as handler:
            handler.write(img_data)
        
        i+= 1