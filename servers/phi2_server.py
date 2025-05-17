import os
import uuid
import torch
from typing import List, Literal
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import time
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# --- Model Setup ---
MODEL_NAME = "microsoft/phi-2"
CACHE_DIR = "models"

# Ensure models directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

print(f"Loading Phi-2 model: {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)

# Set pad token to eos token to allow padding
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float32, cache_dir=CACHE_DIR)
model.eval()
print("Phi-2 model ready.")

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

    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]

    if req.stream:
        def token_stream():
            with torch.no_grad():
                output_ids = model.generate(
                    input_ids,
                    attention_mask=attention_mask,
                    max_new_tokens=req.max_tokens,
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id
                )
                full_output = tokenizer.decode(output_ids[0], skip_special_tokens=True)
                assistant_output = full_output[len(prompt):]

                for char in assistant_output:
                    chunk = {
                        "choices": [{
                            "delta": {
                                "role": "assistant",
                                "content": char
                            },
                            "index": 0
                        }]
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"
                    time.sleep(0.01)

                yield f"data: {json.dumps({'choices': [{'delta': {}, 'finish_reason': 'stop', 'index': 0}]})}\n\n"
        return StreamingResponse(token_stream(), media_type="text/event-stream")
    else:
        with torch.no_grad():
            output_ids = model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_new_tokens=req.max_tokens,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id
            )
            full_output = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            assistant_output = full_output[len(prompt):]
            return {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": assistant_output
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
    inputs = tokenizer(req.prompt, return_tensors="pt", padding=True, truncation=True)
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=req.max_tokens,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id
        )
        full_output = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        completion = full_output[len(req.prompt):]
        return {
            "id": f"cmpl-{uuid.uuid4()}",
            "object": "text_completion",
            "choices": [{
                "text": completion,
                "index": 0,
                "finish_reason": "stop"
            }],
            "model": req.model
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
