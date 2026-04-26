# main.py
import base64
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# ---------- Config ----------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

SYSTEM_PROMPT = (
    "You are an AI lecture assistant. Read the handwritten notes in this image. "
    "If it ends in a '?', directly answer the question. "
    "If it ends in an '=', solve the math equation. "
    "Otherwise, define the main concept written in 1-2 concise sentences. "
    "Return your response formatted clearly."
)

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI(title="iPad Notes AI Backend")


# CORS so iPad Safari can call laptop local IP
# For hackathon speed: allow all origins. You can lock this down later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CanvasPayload(BaseModel):
    image_base64: str  # can be raw base64 OR data URL (data:image/png;base64,...)


class CanvasResponse(BaseModel):
    response: str


def _normalize_base64_to_data_url(image_base64: str) -> str:
    """
    Accepts either:
    - raw base64 string
    - full data URL: data:image/png;base64,....
    Returns data URL string expected by OpenAI image input.
    """
    image_base64 = image_base64.strip()
    if image_base64.startswith("data:image"):
        return image_base64

    # Validate base64 quickly
    try:
        base64.b64decode(image_base64, validate=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {e}")

    return f"data:image/png;base64,{image_base64}"


@app.post("/process_canvas", response_model=CanvasResponse)
def process_canvas(payload: CanvasPayload):
    try:
        image_url = _normalize_base64_to_data_url(payload.image_base64)

        resp = client.responses.create(
            model=MODEL_NAME,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Analyze this handwritten note."},
                        {"type": "input_image", "image_url": image_url},
                    ],
                },
            ],
        )

        text = (resp.output_text or "").strip()
        if not text:
            text = "I couldn't read enough handwriting to respond confidently. Try writing larger/darker."

        return CanvasResponse(response=text)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {e}")


@app.get("/health")
def health():
    return {"ok": True}