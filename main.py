import base64
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import traceback

# ---------- Config ---------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# gemini-2.0-flash has 1,500 free requests/day vs 20 for gemini-2.5-flash
MODEL_NAME = "gemini-2.5-flash-lite"

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
        b64_data = payload.image_base64
        if "," in b64_data:
            b64_data = b64_data.split(",")[1]

        image_bytes = base64.b64decode(b64_data)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                SYSTEM_PROMPT,
                "Analyze this handwritten note.",
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ],
        )

        text = (response.text or "").strip()
        if not text:
            text = "I couldn't read enough handwriting to respond confidently. Try writing larger/darker."

        return CanvasResponse(response=text)

    except Exception as e:
        traceback.print_exc()
        err_str = str(e)
        # Surface quota errors as 429 so the frontend can show a friendlier message
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            raise HTTPException(
                status_code=429,
                detail="API quota exceeded. Wait a minute and try again, or upgrade your Gemini plan.",
            )
        raise HTTPException(status_code=500, detail=f"AI processing failed: {e}")

@app.get("/health")
def health():
    return {"ok": True}