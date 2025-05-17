# llama-devstack-extensible

A lightweight, self-hosted LLM development stack. Intended to be used with Continue.dev to serve local models.

## 🛠 Setup

Use the included batch installer (Windows):

```
.\installer\install.bat
```

This will:
- Create a Python 3.11 virtual environment
- Install all dependencies (CPU-only)
- Set up everything needed to run the server

## 🚀 Run a Model Server

```
.\servers\run_rwkv_server.bat

or

.\servers\run_phi2_server.bat
```

Model files will download on first run.

## 🧠 Use with Continue.dev

Point Continue.dev to:
```
Configure your config.yaml file to look something like this:

name: Local Assistant
version: 1.0.0
schema: v1

models:
  - name: Llama3.1 405b (Free Trial)
    provider: free-trial
    model: llama3.1-405b

  - name: Local
    provider: lmstudio
    model: rwkv
    apiBase: http://localhost:8000/v1
    roles: [chat, autocomplete, edit, apply, rerank]
    
default_model: Local




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
