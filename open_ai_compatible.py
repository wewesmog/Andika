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
                "content": "What is the capital of France?"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat()