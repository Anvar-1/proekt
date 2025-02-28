import requests

def get_location(ip_address):
    response = requests.get(f"http://ip-api.com/json/{ip_address}")
    if response.status_code == 200:
        return response.json()
    return None