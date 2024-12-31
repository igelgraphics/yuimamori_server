import requests
import time

GOOGLE_CLOUD_API_URL = "https://asia-northeast1-yuimamori-server.cloudfunctions.net/function-1"

def sendLocationToGoogleCloud(lat, lon):
    try:
        payload = {
            "latitude": lat,
            "longitude": lon,
            "timestamp": int(time.time())
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(GOOGLE_CLOUD_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            print(f"Location sent to Google Cloud: {response.json()}")
        else:
            print(f"Failed to send location. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending location to Google Cloud: {e}")
