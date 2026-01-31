# Logo Creator

AI-powered logo generation application built with React, TypeScript, and FastAPI.

## Features

- **Text-to-Logo Generation**: Describe your logo and AI generates it
- **Style Presets**: Choose from Minimal, Modern, Playful, Professional, or Vintage
- **Live Preview**: View generated logos on light, dark, or transparent backgrounds
- **Multiple Download Sizes**: Export as PNG in 256px, 512px, or 1024px
- **Transparent Background Option**: Download with or without background

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- TanStack Query (React Query) for data fetching
- Lucide React for icons

### Backend
- Python FastAPI
- OpenAI DALL-E 3 for image generation
- Pillow for image processing
- Rate limiting (10 requests/minute per IP)

## Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- OpenAI API key (optional - app works with placeholders for testing)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key (optional)
export OPENAI_API_KEY=your-api-key-here

# Run server
python main.py
# Or: uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend runs on http://localhost:5173 and proxies API requests to http://localhost:8000.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check with OpenAI status |
| `/api/styles` | GET | List available style presets |
| `/api/generate` | POST | Generate a logo |
| `/api/download` | POST | Process and download logo |

### Generate Logo

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A modern tech startup logo for Nexus AI",
    "style": "modern"
  }'
```

### Download Logo

```bash
curl -X POST http://localhost:8000/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "...",
    "size": 512,
    "transparent": true
  }' --output logo.png
```

## Project Structure

```
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LogoForm.tsx      # Input form with description + style
│   │   │   ├── LogoPreview.tsx   # Preview with zoom + background toggle
│   │   │   ├── DownloadPanel.tsx # Size selection + download button
│   │   │   └── StyleSelector.tsx # Style preset chips
│   │   ├── api.ts                # API client functions
│   │   ├── types.ts              # TypeScript types
│   │   ├── App.tsx               # Main application
│   │   └── main.tsx              # Entry point
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── main.py                   # FastAPI application
│   └── requirements.txt
└── APP_README.md
```

## Development Notes

- Without an OpenAI API key, the app generates placeholder images for testing
- Rate limiting is set to 10 requests per minute per IP
- Images are generated at 1024x1024 and can be resized on download
- CORS is configured for localhost development

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No | OpenAI API key for real logo generation |

## License

MIT
