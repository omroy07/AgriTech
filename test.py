import requests

url = "http://127.0.0.1:5000/recognize"
files = {"image": open("shubhangi1.jpeg", "rb")}

r = requests.post(url, files=files)
print(r.json())
