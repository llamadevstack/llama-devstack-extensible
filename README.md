# llama-devstack

A lightweight, self-hosted LLM development stack using TinyLlama and `llama-cpp-python`. Python 3.13 compatible.

## 🛠 Setup

Use the included batch installer (Windows):

```
scripts\install.bat
```

This will:
- Create a virtual environment
- Install all dependencies (CPU-only)
- Set up everything needed to run the server

## 🚀 Run the Model Server

```
venv\Scripts\activate
python llama_devstack_server.py
```

The model will download on first run (~500MB).

## 🧠 Use with Continue.dev

Point Continue.dev to:
```
http://localhost:8000/generate
```

Request format:
```json
{ "prompt": "your prompt", "max_tokens": 128 }
```
Response format:
```json
{ "response": "your model output" }
```

---

## 🧠 Option 3: RWKV (Pure Python, Works with Python 3.13)

If you want to avoid C++ build issues and stay in Python 3.13, run a lightweight RWKV model instead:

### Setup

1. Download this model file (approx 140MB):
   [RWKV-4-World-0.1B](https://huggingface.co/BlinkDL/rwkv-4-world)

2. Save it to:
   ```
   models/RWKV-4-World-0.1B-v1-20230626-ctx4096.pth
   ```

3. Run the server:

   ```
   python rwkv_server.py
   ```

4. Use `/generate` just like the LLaMA version:

   ```json
   POST http://localhost:8000/generate
   {
     "prompt": "What is llama-devstack?",
     "max_tokens": 100
   }
   ```

This version uses no compiled extensions and works on all Python 3.13 systems.
