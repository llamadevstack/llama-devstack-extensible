
import requests
import json

base_url = "http://127.0.0.1:8000"

def validate_completion_response(resp):
    assert "choices" in resp, "Missing 'choices'"
    assert isinstance(resp["choices"], list), "'choices' should be a list"
    assert "text" in resp["choices"][0], "Missing 'text' in choices[0]"
    print("✅ Completion response shape is valid.")

def validate_chat_response(resp):
    assert "choices" in resp, "Missing 'choices'"
    assert isinstance(resp["choices"], list), "'choices' should be a list"
    assert "message" in resp["choices"][0], "Missing 'message' in choices[0]"
    assert "content" in resp["choices"][0]["message"], "Missing 'content' in message"
    print("✅ Chat response shape is valid.")

def test_completion():
    print("\nTesting /v1/completions...")
    data = {
        "model": "rwkv",
        "prompt": "Once upon a time,",
        "max_tokens": 50
    }
    response = requests.post(f"{base_url}/v1/completions", json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    assert response.status_code == 200, "Expected 200 OK"
    validate_completion_response(response.json())

def test_chat_completion():
    print("\nTesting /v1/chat/completions...")
    data = {
        "model": "rwkv",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "max_tokens": 50,
        "stream": False
    }
    response = requests.post(f"{base_url}/v1/chat/completions", json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    assert response.status_code == 200, "Expected 200 OK"
    validate_chat_response(response.json())

def test_streaming_chat_completion():
    print("\nTesting /v1/chat/completions with stream=True...")
    data = {
        "model": "rwkv",
        "messages": [{"role": "user", "content": "Write a short poem about the stars."}],
        "max_tokens": 50,
        "stream": True
    }
    with requests.post(f"{base_url}/v1/chat/completions", json=data, stream=True) as response:
        print("Status Code:", response.status_code)
        assert response.status_code == 200, "Expected 200 OK"
        print("Streamed Response:")
        found_token = False
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                print(decoded)
                if '"content":' in decoded:
                    found_token = True
        assert found_token, "Expected at least one content token in streaming output"
        print("✅ Streaming response produced content.")

def test_missing_fields():
    print("\nTesting missing field error...")
    data = {
        "model": "rwkv"
        # missing prompt or messages
    }
    response = requests.post(f"{base_url}/v1/completions", json=data)
    print("Status Code:", response.status_code)
    assert response.status_code == 422, "Expected 422 for malformed request"
    print("✅ Properly handled missing field with 422.")

if __name__ == "__main__":
    try:
        test_completion()
        test_chat_completion()
        test_streaming_chat_completion()
        test_missing_fields()
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server at", base_url)
        print("Make sure your RWKV server is running.")
    except AssertionError as e:
        print("Test failed:", e)
