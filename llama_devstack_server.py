import os
import requests
from tqdm import tqdm
from fastapi import FastAPI
from pydantic import BaseModel
from llama_cpp import Llama

MODEL_DIR = "models"
MODEL_FILENAME = "tinyllama-1.1b-chat.q4_K_M.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat.q4_K_M.gguf?download=true"

def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"Downloading model to {MODEL_PATH}...")
    response = requests.get(MODEL_URL, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    with open(MODEL_PATH, 'wb') as file, tqdm(
        desc=MODEL_FILENAME,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
            bar.update(len(data))
    print("Download complete.")

if not os.path.exists(MODEL_PATH):
    download_model()

print("Loading model...")
llm = Llama(model_path=MODEL_PATH, n_ctx=512)
print("Model ready.")

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 128

@app.post("/generate")
async def generate_text(req: PromptRequest):
    output = llm(
        req.prompt,
        max_tokens=req.max_tokens,
        stop=["</s>"],
        echo=False
    )
    return {"response": output["choices"][0]["text"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("llama_devstack_server:app", host="127.0.0.1", port=8000)
