import requests

def test_chat():
    url = "http://212.56.44.75:8001/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "custom-model",

        
        "messages": [
            {
                "role": "user",
                "content": "What is Okolea loan?"
            }
        ]
    }

    try:
        print(f"Sending request to: {url}")
        print(f"Payload: {payload}")
        
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response Headers:", dict(response.headers))
        print("Response Body:", response.text)
        
        if response.status_code == 200:
            print("Parsed JSON Response:", response.json())
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    test_chat() 