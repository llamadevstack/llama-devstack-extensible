# llama-devstack-extensible

A lightweight, self-hosted LLM development stack. Intended to be used with Continue.dev to serve local models.

## 📦 Prerequisites

Before setting up the project, ensure you have the following software installed:

1. **Visual Studio Code**
   - Download: [https://code.visualstudio.com/](https://code.visualstudio.com/)

2. **Node.js**
   - Download: [https://nodejs.org/](https://nodejs.org/)

3. **Python**
   - Any version of Python is required for general use.
   - Python 3.11 is specifically required for this project.
   - Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)

4. **Continue.dev Plugin for VS Code**
   - Install the Continue.dev plugin from the Visual Studio Code Marketplace.
   - Marketplace Link: [https://marketplace.visualstudio.com/items?itemName=Continue.continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue)

Ensure all the above software is installed and properly configured before proceeding with the setup.

## 📂 Quick Start with NPX

You can quickly set up this project in a new directory using a single `npx` command. This will clone the repository and prepare the environment for you.

1. Open a terminal and run the following command:
   ```bash
   npx degit llamadevstack/llama-devstack-extensible my-llama-project
   ```

   - This will create a new directory named `my-llama-project` and copy the project files into it.
   - Replace `my-llama-project` with your desired directory name if needed.

2. Navigate to the project directory:
   ```bash
   cd my-llama-project
   ```

3. Follow the setup instructions in the [Setup](#-setup) section to complete the installation.

## 🛠 Setup

Use the included batch installer (Windows):

```
.\installer\install.bat
```

This will:
- Create a Python 3.11 virtual environment
- Install all dependencies (CPU-only)
- Set up everything needed to run the server

### Advanced Setup

For Linux or macOS users, consider using a Python virtual environment manually:

1. Install Python 3.11.
2. Create a virtual environment:
   ```bash
   python3.11 -m venv venv
   ```
3. Activate the virtual environment:
   - Linux/macOS: `source venv/bin/activate`
   - Windows: `venv\Scripts\Activate.ps1`
4. Install dependencies:
   ```bash
   pip install -r installer/pythonrequirements.txt
   ```

## 🚀 Run a Model Server

Run one of the following commands to start a server on port 8000:

```
.\servers\run_rwkv_server.bat

or

.\servers\run_phi2_server.bat
```

Model files will download on first run.

## 🚀 Run a Proxy Server to return token counts

The proxy server will return token counts.  Run this command to start a node express server on port 3000 that will call the server on port 8000:

```

.\proxy-server\run_proxy_server.bat

```

### API Endpoints

The servers provide OpenAI-compatible endpoints:

1. **Chat Completions** (`/v1/chat/completions`):
   - Request:
     ```json
     {
       "model": "rwkv",
       "messages": [
         {"role": "user", "content": "Hello!"}
       ],
       "max_tokens": 50
     }
     ```
   - Response:
     ```json
     {
       "id": "chatcmpl-123",
       "object": "chat.completion",
       "choices": [
         {
           "index": 0,
           "message": {"role": "assistant", "content": "Hi there!"},
           "finish_reason": "stop"
         }
       ],
       "model": "rwkv"
     }
     ```

2. **Text Completions** (`/v1/completions`):
   - Request:
     ```json
     {
       "model": "rwkv",
       "prompt": "Once upon a time,",
       "max_tokens": 50
     }
     ```
   - Response:
     ```json
     {
       "id": "cmpl-123",
       "object": "text_completion",
       "choices": [
         {
           "text": " there was a brave knight.",
           "index": 0,
           "finish_reason": "stop"
         }
       ],
       "model": "rwkv"
     }
     ```

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
    apiBase: http://127.0.0.1:8000/v1
    roles: [chat, autocomplete, edit, apply]

  - name: Local (Token Usage via Node)
    provider: lmstudio
    model: rwkv
    apiBase: http://127.0.0.1:3000/v1
    roles: [chat, autocomplete, edit, apply]
    
default_model: Local
```

## 🔧 Extending the Project

### Adding a New Model

1. Place the model files in the `models/` directory.
2. Create a new server script in the `servers/` directory.
3. Follow the structure of `rwkv_server.py` or `phi2_server.py` to implement the model.
4. Add a batch and PowerShell script to start the server.

### Customizing Endpoints

1. Modify the FastAPI app in the server script.
2. Add new routes or extend existing ones as needed.

## 🛡 Security

- Add authentication to the API endpoints for production use.
- Use HTTPS for secure communication.

## 🚀 Deployment

### Local Deployment

1. Run the server scripts directly on your machine.
2. Use tools like `ngrok` to expose the server to the internet for testing.

### Cloud Deployment

1. Use Docker to containerize the application.
2. Deploy to cloud platforms like AWS, Azure, or Google Cloud.
3. Use Kubernetes for scaling and orchestration.

## 🧪 Testing

Run the test scripts to validate the server:

```
python servers/test/test_lmstudio_server.py
```

This will:
- Test the `/v1/completions` and `/v1/chat/completions` endpoints.
- Validate response formats and error handling.

## 🧠 Supported Models

### RWKV
- Lightweight and efficient.
- Suitable for CPU-only environments.

### Phi-2
- Larger and more powerful.
- Requires GPU for optimal performance.

## 🗑 Cleanup

To remove unused models or reset the environment:

1. Delete the `models/` directory.
2. Re-run the setup script.
