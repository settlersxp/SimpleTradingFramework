import requests

BASE_URL = "http://localhost:3100"


response = requests.post(f"{BASE_URL}/trades/")
print(response.json())

response = requests.post(f"{BASE_URL}/trades")
print(response.json())