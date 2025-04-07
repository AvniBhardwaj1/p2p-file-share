import requests

def get_public_ip():
    url = "https://api.ipify.org?format=json"
    response = requests.get(url)
    if response.status_code == 200:
        ip = response.json().get('ip')
        return ip
    else:
        return "Error: Unable to fetch IP"

# Get the public IP and print it
ip = get_public_ip()
print(f"Your public IP is: {ip}")
