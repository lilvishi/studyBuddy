import base64
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# ---------- Config ----------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = (
    "You are an AI lecture assistant. Read the handwritten notes in this image. "
    "If it ends in a '?', directly answer the question. "
    "If it ends in an '=', solve the math equation. "
    "Otherwise, define the main concept written in 1-2 concise sentences. "
    "Return your response formatted clearly."
)

if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY environment variable.")

client = genai.Client(api_key=GEMINI_API_KEY)
app = FastAPI(title="iPad Notes AI Backend")

# CORS so iPad Safari can call laptop local IP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CanvasPayload(BaseModel):
    image_base64: str

class CanvasResponse(BaseModel):
    response: str

@app.post("/process_canvas", response_model=CanvasResponse)
def process_canvas(payload: CanvasPayload):
    try:
        # 1. Clean the base64 string (remove the "data:image/png;base64," prefix from the HTML canvas)
        b64_data = payload.image_base64
        if "," in b64_data:
            b64_data = b64_data.split(",")[1]

        # 2. Decode into raw bytes
        image_bytes = base64.b64decode(b64_data)

        # 3. Call Gemini
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                SYSTEM_PROMPT,
                "Analyze this handwritten note.",
                types.Part.from_bytes(data=image_bytes, mime_type='image/png')
            ]
        )

        text = (response.text or "").strip()
        if not text:
            text = "I couldn't read enough handwriting to respond confidently. Try writing larger/darker."

        return CanvasResponse(response=text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {e}")

@app.get("/health")
def health():
    return {"ok": True}