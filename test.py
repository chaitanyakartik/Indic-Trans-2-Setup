import requests
import time

print("Testing health endpoint...")

for i in range(5):
    try:
        response = requests.get("http://localhost:8003/health", timeout=2)
        print(f"Attempt {i+1}: Status {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Server is ready!")
            break
    except Exception as e:
        print(f"Attempt {i+1}: Error - {e}")
    
    time.sleep(1)

# Now try a translation
print("\nTrying translation...")
try:
    response = requests.post(
        "http://localhost:8003/translate",
        json={
            "source_language": "eng_Latn",
            "target_language": "kan_Knda",
            "text": "Hello world"
        },
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
