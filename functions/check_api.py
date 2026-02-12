import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def check_endpoint(endpoint):
    print(f"Checking {endpoint}...")
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            try:
                print("Error Details:", response.json())
            except:
                print("Response Text:", response.text)
        else:
            print("Success")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    check_endpoint("/api/courses")
    check_endpoint("/api/stats")
