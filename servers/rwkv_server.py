import os
import requests
import uuid
from typing import List, Literal

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from rwkv.model import RWKV
from rwkv.utils import PIPELINE, PIPELINE_ARGS
from tqdm import tqdm
import time
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# --- Model Setup ---
MODEL_DIR = "models"
MODEL_FILENAME = "RWKV-4-World-0.1B-v1-20230520-ctx4096.pth"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
MODEL_URL = "https://huggingface.co/BlinkDL/rwkv-4-world/resolve/main/RWKV-4-World-0.1B-v1-20230520-ctx4096.pth"

def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"Downloading RWKV model to {MODEL_PATH}...")
    response = requests.get(MODEL_URL, stream=True, headers={"User-Agent": "Mozilla/5.0"})
    total_size = int(response.headers.get("content-length", 0))
    with open(MODEL_PATH, "wb") as file, tqdm(
        desc=MODEL_FILENAME,
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
            bar.update(len(data))
    print("Download complete.")
    with open(MODEL_PATH, "rb") as f:
        first_bytes = f.read(20)
        if first_bytes.startswith(b"<!DOCTYPE") or os.path.getsize(MODEL_PATH) < 1000000:
            os.remove(MODEL_PATH)
            raise ValueError("Downloaded file is not a valid model.")

if not os.path.exists(MODEL_PATH):
    download_model()

print("Loading RWKV model...")
model = RWKV(model=MODEL_PATH, strategy="cpu fp32")
pipeline = PIPELINE(model, "rwkv_vocab_v20230424")
print("RWKV model ready.")

# --- FastAPI Setup ---
app = FastAPI()

# --- OpenAI-compatible Chat Completion Endpoint ---
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: int = 100
    stream: bool = False

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, req: ChatCompletionRequest):
    logging.debug(f"Received request body: {req}")
    prompt = "\n".join([m.content for m in req.messages if m.role == "user"])
    args = PIPELINE_ARGS(temperature=1.0, top_p=0.8, top_k=40)

    if req.stream:
        def token_stream():
            try:
                for token in pipeline.generate(prompt, token_count=req.max_tokens, args=args):
                    chunk = {
                        "choices": [{
                            "delta": {
                                "role": "assistant",
                                "content": token
                            },
                            "index": 0
                        }]
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"
                    time.sleep(0.01)
                # Final stop message
                yield f"data: {json.dumps({'choices': [{'delta': {}, 'finish_reason': 'stop', 'index': 0}]})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(token_stream(), media_type="text/event-stream")

    else:
        output = pipeline.generate(prompt, token_count=req.max_tokens, args=args)
        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": output
                },
                "finish_reason": "stop"
            }],
            "model": req.model
        }

# --- OpenAI-compatible Completion Endpoint for Autocomplete ---
class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

@app.post("/v1/completions")
async def completions(request: Request, req: CompletionRequest):
    logging.debug(f"Received request body: {req}")
    args = PIPELINE_ARGS(temperature=1.0, top_p=0.8, top_k=40)
    output = pipeline.generate(req.prompt, token_count=req.max_tokens, args=args)
    return {
        "id": f"cmpl-{uuid.uuid4()}",
        "object": "text_completion",
        "choices": [{
            "text": output,
            "index": 0,
            "finish_reason": "stop"
        }],
        "model": req.model
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rwkv_server:app", host="127.0.0.1", port=8000, reload=True,  reload_includes=["rwkv_server.py"])
