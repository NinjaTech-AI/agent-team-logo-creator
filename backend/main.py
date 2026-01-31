"""
Logo Creator API - FastAPI Backend
Handles logo generation requests using AI image generation.
"""

import os
import io
import base64
import time
import hashlib
from datetime import datetime
from typing import Optional
from enum import Enum

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from PIL import Image
import httpx

app = FastAPI(
    title="Logo Creator API",
    description="AI-powered logo generation API",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting storage (in production, use Redis)
rate_limit_store: dict[str, list[float]] = {}
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW = 60  # seconds


class StylePreset(str, Enum):
    MINIMAL = "minimal"
    MODERN = "modern"
    PLAYFUL = "playful"
    PROFESSIONAL = "professional"
    VINTAGE = "vintage"


class LogoRequest(BaseModel):
    """Request model for logo generation."""
    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Text description of the desired logo"
    )
    style: Optional[StylePreset] = Field(
        default=None,
        description="Optional style preset to guide generation"
    )


class LogoResponse(BaseModel):
    """Response model for generated logo."""
    image_base64: str
    style_applied: Optional[str]
    generation_time_ms: int
    prompt_used: str


class DownloadRequest(BaseModel):
    """Request model for logo download."""
    image_base64: str
    size: int = Field(default=512, description="Size in pixels (256, 512, or 1024)")
    transparent: bool = Field(default=True, description="Include transparency")


def get_client_ip(request: Request) -> str:
    """Get client IP for rate limiting."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit."""
    now = time.time()
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []

    # Remove old timestamps
    rate_limit_store[client_ip] = [
        ts for ts in rate_limit_store[client_ip]
        if now - ts < RATE_LIMIT_WINDOW
    ]

    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False

    rate_limit_store[client_ip].append(now)
    return True


def build_prompt(description: str, style: Optional[StylePreset]) -> str:
    """Build the full prompt for logo generation."""
    style_modifiers = {
        StylePreset.MINIMAL: "minimalist, clean lines, simple shapes, limited colors, white space",
        StylePreset.MODERN: "modern, sleek, geometric, bold colors, contemporary design",
        StylePreset.PLAYFUL: "playful, colorful, fun, friendly, rounded shapes, vibrant",
        StylePreset.PROFESSIONAL: "professional, corporate, trustworthy, refined, elegant",
        StylePreset.VINTAGE: "vintage, retro, classic, nostalgic, hand-drawn feel, muted colors",
    }

    base_prompt = f"Logo design: {description}. High quality, vector-style, centered composition, suitable for business use, clean background."

    if style and style in style_modifiers:
        base_prompt = f"{base_prompt} Style: {style_modifiers[style]}."

    return base_prompt


async def generate_logo_with_openai(prompt: str) -> str:
    """Generate logo using OpenAI DALL-E API."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured"
        )

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024",
                    "quality": "standard",
                    "response_format": "b64_json"
                }
            )

            if response.status_code != 200:
                error_detail = response.json().get("error", {}).get("message", "Unknown error")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API error: {error_detail}"
                )

            data = response.json()
            return data["data"][0]["b64_json"]

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Logo generation timed out. Please try again."
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to AI service: {str(e)}"
            )


def generate_placeholder_logo(description: str, style: Optional[StylePreset]) -> str:
    """Generate a placeholder logo when API is not available (for testing)."""
    # Create a simple colored square with text as placeholder
    from PIL import Image, ImageDraw, ImageFont

    # Color based on style
    colors = {
        StylePreset.MINIMAL: (240, 240, 240),
        StylePreset.MODERN: (0, 120, 215),
        StylePreset.PLAYFUL: (255, 107, 107),
        StylePreset.PROFESSIONAL: (51, 51, 51),
        StylePreset.VINTAGE: (139, 90, 43),
        None: (100, 100, 100),
    }

    bg_color = colors.get(style, (100, 100, 100))
    img = Image.new('RGBA', (512, 512), bg_color + (255,))
    draw = ImageDraw.Draw(img)

    # Add some visual interest
    for i in range(5):
        offset = 50 + i * 20
        shape_color = tuple(min(c + 30, 255) for c in bg_color) + (150,)
        draw.ellipse([offset, offset, 512-offset, 512-offset], outline=shape_color, width=2)

    # Add text
    text = description[:20] + "..." if len(description) > 20 else description
    text_color = (255, 255, 255) if sum(bg_color) < 400 else (0, 0, 0)

    # Center text (approximate)
    text_x = 256
    text_y = 256
    draw.text((text_x, text_y), text, fill=text_color, anchor="mm")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Logo Creator API"}


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "openai_configured": bool(os.environ.get("OPENAI_API_KEY"))
    }


@app.post("/api/generate", response_model=LogoResponse)
async def generate_logo(request: Request, logo_request: LogoRequest):
    """
    Generate a logo based on text description.

    - **description**: Text describing the desired logo (10-500 characters)
    - **style**: Optional style preset (minimal, modern, playful, professional, vintage)
    """
    # Rate limiting
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before generating more logos."
        )

    start_time = time.time()
    prompt = build_prompt(logo_request.description, logo_request.style)

    # Try OpenAI first, fall back to placeholder
    try:
        if os.environ.get("OPENAI_API_KEY"):
            image_base64 = await generate_logo_with_openai(prompt)
        else:
            # Use placeholder for development/testing
            image_base64 = generate_placeholder_logo(
                logo_request.description,
                logo_request.style
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate logo: {str(e)}"
        )

    generation_time = int((time.time() - start_time) * 1000)

    return LogoResponse(
        image_base64=image_base64,
        style_applied=logo_request.style.value if logo_request.style else None,
        generation_time_ms=generation_time,
        prompt_used=prompt
    )


@app.post("/api/download")
async def download_logo(download_request: DownloadRequest):
    """
    Process and download a logo at specified size.

    - **image_base64**: Base64 encoded image data
    - **size**: Output size in pixels (256, 512, or 1024)
    - **transparent**: Whether to preserve transparency
    """
    # Validate size
    valid_sizes = [256, 512, 1024]
    if download_request.size not in valid_sizes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid size. Must be one of: {valid_sizes}"
        )

    try:
        # Decode base64 image
        image_data = base64.b64decode(download_request.image_base64)
        img = Image.open(io.BytesIO(image_data))

        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Resize if needed
        if img.size != (download_request.size, download_request.size):
            img = img.resize(
                (download_request.size, download_request.size),
                Image.Resampling.LANCZOS
            )

        # Handle transparency
        if not download_request.transparent:
            # Add white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Save to buffer
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)

        # Generate filename
        filename = f"logo_{download_request.size}px.png"

        return StreamingResponse(
            buffer,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process image: {str(e)}"
        )


@app.get("/api/styles")
async def get_styles():
    """Get available style presets with descriptions."""
    return {
        "styles": [
            {
                "id": "minimal",
                "name": "Minimal",
                "description": "Clean lines, simple shapes, limited colors"
            },
            {
                "id": "modern",
                "name": "Modern",
                "description": "Sleek, geometric, bold and contemporary"
            },
            {
                "id": "playful",
                "name": "Playful",
                "description": "Colorful, fun, friendly and vibrant"
            },
            {
                "id": "professional",
                "name": "Professional",
                "description": "Corporate, trustworthy, refined and elegant"
            },
            {
                "id": "vintage",
                "name": "Vintage",
                "description": "Retro, classic, nostalgic feel"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
