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
    description: str | None = None  # #32: Story/description field
    size: str | None = "1024x1024"  # #33: Size selection
    resolution: str | None = "high"  # #33: Resolution selection
    filters: list[str] | None = None  # #34: Image filters/effects
    transparency: bool | None = False  # #36: Transparency toggle
    preview_mode: bool | None = False  # #35: Quick preview mode


class ImprovePromptRequest(BaseModel):
    business_name: str
    style: str
    description: str | None = None
    current_prompt: str | None = None


class ImprovePromptResponse(BaseModel):
    success: bool
    improved_prompt: str | None = None
    preview_url: str | None = None
    error: str | None = None


class GenerateLogoResponse(BaseModel):
    success: bool
    logo_url: str | None = None  # Deprecated: kept for backward compatibility
    logo_urls: list[str] | None = None  # New: multiple logo URLs
    generation_id: str | None = None
    error: str | None = None


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/improve-prompt", response_model=ImprovePromptResponse)
async def improve_prompt(request: ImprovePromptRequest):
    """#37: AI Prompt Improver - Enhance user's prompt with AI suggestions"""
    try:
        client = get_openai_client()
        
        # Build context for prompt improvement
        context = f"Business Name: {request.business_name}\nStyle: {request.style}"
        if request.description:
            context += f"\nDescription: {request.description}"
        if request.current_prompt:
            context += f"\nCurrent Prompt: {request.current_prompt}"
        
        # Use GPT-4 to improve the prompt
        improvement_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert logo designer and prompt engineer. Your task is to improve logo generation prompts to create better, more professional logos. Focus on clarity, visual appeal, and brand identity."
                },
                {
                    "role": "user",
                    "content": f"""Improve this logo generation prompt:

{context}

Create an enhanced prompt that will generate a better logo. Include:
- Clear visual style and aesthetic
- Color palette suggestions
- Typography considerations
- Brand personality
- Professional design principles

Return ONLY the improved prompt text, no explanations."""
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        improved_prompt = improvement_response.choices[0].message.content.strip()

        # Generate preview with improved prompt using DALL-E 3
        preview_response = client.images.generate(
            model="dall-e-3",
            prompt=improved_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        preview_url = preview_response.data[0].url

        return ImprovePromptResponse(
            success=True,
            improved_prompt=improved_prompt,
            preview_url=preview_url
        )

    except Exception as e:
        return ImprovePromptResponse(
            success=False,
            error=f"Failed to improve prompt: {str(e)}"
        )


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

        # Base prompt
        prompt = f"""Create a professional logo for a company called "{request.business_name}".
Style: {style_desc}"""

        # #32: Add description/story if provided
        if request.description:
            prompt += f"\nBrand Story: {request.description}"

        # #34: Add filters/effects if specified
        if request.filters and len(request.filters) > 0:
            filters_desc = ", ".join(request.filters)
            prompt += f"\nVisual Effects: {filters_desc}"

        # #36: Add transparency requirement
        if request.transparency:
            prompt += "\nBackground: transparent or white background suitable for transparency"
        else:
            prompt += "\nBackground: clean white or subtle gradient background"

        prompt += """
Requirements:
- Clean, scalable design suitable for a business logo
- Simple background
- Text should be clearly readable if included
- Professional and memorable design
- Suitable for use on websites, business cards, and marketing materials"""

        # #33: Validate and set size
        valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
        size = request.size if request.size in valid_sizes else "1024x1024"
        
        # #35: Preview mode uses smaller size and low quality
        if request.preview_mode:
            size = "1024x1024"
            quality = "low"
        else:
            # Map quality values to OpenAI's accepted values: low, medium, high, auto
            quality_map = {
                "standard": "medium",
                "high": "high",
                "hd": "high"
            }
            quality = quality_map.get(request.resolution, "high")

        # Generate image using OpenAI DALL-E 3 API
        client = get_openai_client()

        # DALL-E 3 only supports 1024x1024, 1792x1024, 1024x1792
        dalle_size = size if size in ["1024x1024", "1792x1024", "1024x1792"] else "1024x1024"
        # DALL-E 3 only supports "standard" and "hd" quality
        dalle_quality = "hd" if quality in ["high", "hd"] else "standard"

        # Determine number of variations (4 for full generation, 1 for preview)
        # DALL-E 3 only supports n=1, so we need to make multiple calls
        num_variations = 1 if request.preview_mode else 4
        
        logo_urls = []
        for i in range(num_variations):
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=dalle_size,
                quality=dalle_quality,
                n=1,
            )
            logo_urls.append(response.data[0].url)

        return GenerateLogoResponse(
            success=True,
            logo_url=logo_urls[0] if logo_urls else None,  # Backward compatibility
            logo_urls=logo_urls,
            generation_id=generation_id,
        )

    except Exception as e:
        return GenerateLogoResponse(
            success=False,
            error=f"Failed to generate logo: {str(e)}",
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