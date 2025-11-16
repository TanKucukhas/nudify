"""
FastAPI server for image generation.
"""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .models import GenerateRequest, GenerateResponse, ImageMetadata
from .comfyui_client import ComfyUIClient

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Image Generation Lab API",
    description="Clean API for ComfyUI-backed image generation",
    version="1.0.0"
)

# Initialize ComfyUI client
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://localhost:8188")
comfyui = ComfyUIClient(base_url=COMFYUI_URL)

# Base directory for results
RESULTS_DIR = Path(os.getenv("RESULTS_DIR", "results_dev"))


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Image Generation Lab API",
        "version": "1.0.0",
        "endpoints": {
            "/generate": "POST - Generate an image",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    comfyui_ok = comfyui.health_check()

    return {
        "status": "healthy" if comfyui_ok else "degraded",
        "comfyui": "connected" if comfyui_ok else "disconnected",
        "comfyui_url": COMFYUI_URL
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate an image using ComfyUI.

    This endpoint accepts a generation request and returns the path to the
    generated image along with metadata.
    """
    try:
        # Check ComfyUI availability
        if not comfyui.health_check():
            raise HTTPException(
                status_code=503,
                detail=f"ComfyUI is not available at {COMFYUI_URL}"
            )

        # Create output directory for this experiment
        output_dir = RESULTS_DIR / request.experiment_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate the image
        image_path, metadata = comfyui.generate_image(request, output_dir)

        # Build response
        response = GenerateResponse(
            ok=True,
            experiment_id=request.experiment_id,
            stage=request.stage,
            image_path=image_path,
            metadata=ImageMetadata(**metadata)
        )

        return response

    except TimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail=f"Image generation timed out: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating image: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": str(exc),
            "detail": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"Starting server on {host}:{port}")
    print(f"ComfyUI URL: {COMFYUI_URL}")
    print(f"Results directory: {RESULTS_DIR}")

    uvicorn.run(
        "backend.server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
