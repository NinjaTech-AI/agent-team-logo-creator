import os
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Logo Creator API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client (initialized lazily)
_client = None

def get_openai_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client


class GenerateLogoRequest(BaseModel):
    business_name: str
    style: str | None = "modern"


class GenerateLogoResponse(BaseModel):
    success: bool
    logo_url: str | None = None
    generation_id: str | None = None
    error: str | None = None


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/generate", response_model=GenerateLogoResponse)
async def generate_logo(request: GenerateLogoRequest):
    try:
        generation_id = str(uuid.uuid4())

        # Build the prompt for logo generation
        style_prompts = {
            "minimalist": "minimalist, clean lines, simple shapes, limited colors, flat design",
            "modern": "modern, sleek, contemporary, gradient colors, professional",
            "classic": "classic, traditional, elegant, timeless design, refined",
            "playful": "playful, fun, colorful, creative, dynamic shapes",
            "professional": "professional, corporate, trustworthy, clean, business-oriented",
            "vintage": "vintage, retro, nostalgic, classic typography, warm colors",
        }

        style_desc = style_prompts.get(request.style, style_prompts["modern"])

        prompt = f"""Create a professional logo for a company called "{request.business_name}".
Style: {style_desc}
Requirements:
- Clean, scalable design suitable for a business logo
- Simple background (white or transparent preferred)
- Text should be clearly readable if included
- Professional and memorable design
- Suitable for use on websites, business cards, and marketing materials"""

        # Generate image using OpenAI API (GPT Image Generator 1.5 / DALL-E)
        client = get_openai_client()
        response = client.images.generate(
            model="gpt-image-1",  # GPT Image Generator 1.5
            prompt=prompt,
            size="1024x1024",
            quality="high",
            n=1,
        )

        logo_url = response.data[0].url

        return GenerateLogoResponse(
            success=True,
            logo_url=logo_url,
            generation_id=generation_id,
        )

    except Exception as e:
        error_message = str(e)
        # Try fallback to dall-e-3 if gpt-image-1 isn't available
        if "model" in error_message.lower():
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="hd",
                    n=1,
                )
                logo_url = response.data[0].url
                return GenerateLogoResponse(
                    success=True,
                    logo_url=logo_url,
                    generation_id=generation_id,
                )
            except Exception as fallback_e:
                error_message = str(fallback_e)

        return GenerateLogoResponse(
            success=False,
            error=f"Failed to generate logo: {error_message}",
        )


# Serve static frontend files (for production)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API routes are handled above, this catches all other routes for SPA
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
