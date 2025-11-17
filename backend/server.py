"""
FastAPI server for image generation.
"""
import os
import json
import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import queue

from .models import GenerateRequest, GenerateResponse, ImageMetadata, BatchRequest
from .comfyui_client import ComfyUIClient
from .model_manager import ModelManager
from .job_manager import job_manager, JobStatus

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Image Generation Lab API",
    description="Clean API for ComfyUI-backed image generation",
    version="1.0.0"
)

# Enable CORS for Next.js admin panel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:4000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ComfyUI client
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://localhost:8188")
comfyui = ComfyUIClient(base_url=COMFYUI_URL)

# Base directory for results
RESULTS_DIR = Path(os.getenv("RESULTS_DIR", "results_dev"))

# Initialize Model Manager
model_manager = ModelManager(comfyui_url=COMFYUI_URL)


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


@app.post("/api/generate/stream")
async def generate_stream(request: GenerateRequest):
    """
    Generate an image using ComfyUI with Server-Sent Events (SSE) for real-time progress.

    This endpoint streams progress updates during generation and returns the final result.
    """
    async def event_generator():
        progress_queue = queue.Queue()

        def progress_callback(data: dict):
            """Callback to capture progress updates from ComfyUI client."""
            progress_queue.put(data)

        def generate_in_thread():
            """Run the actual generation in a separate thread."""
            try:
                # Check ComfyUI availability
                if not comfyui.health_check():
                    progress_queue.put({
                        "status": "error",
                        "message": f"ComfyUI is not available at {COMFYUI_URL}",
                        "error": True
                    })
                    return

                # Create output directory for this experiment
                output_dir = RESULTS_DIR / request.experiment_id
                output_dir.mkdir(parents=True, exist_ok=True)

                # Generate the image with progress callback
                image_path, metadata = comfyui.generate_image(
                    request,
                    output_dir,
                    progress_callback=progress_callback
                )

                # Send final success message
                progress_queue.put({
                    "status": "success",
                    "message": "Generation complete",
                    "progress": 1.0,
                    "image_path": image_path,
                    "metadata": metadata,
                    "done": True
                })

            except TimeoutError as e:
                progress_queue.put({
                    "status": "error",
                    "message": f"Image generation timed out: {str(e)}",
                    "error": True,
                    "done": True
                })
            except Exception as e:
                progress_queue.put({
                    "status": "error",
                    "message": f"Error generating image: {str(e)}",
                    "error": True,
                    "done": True
                })

        # Start generation in background thread
        import threading
        gen_thread = threading.Thread(target=generate_in_thread, daemon=True)
        gen_thread.start()

        # Stream progress updates
        while True:
            try:
                # Wait for progress update (with timeout to allow checking if done)
                try:
                    progress_data = progress_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                # Send SSE event
                yield f"data: {json.dumps(progress_data)}\n\n"

                # Check if generation is complete
                if progress_data.get("done") or progress_data.get("error"):
                    break

            except Exception as e:
                yield f"data: {json.dumps({'status': 'error', 'message': str(e), 'error': True, 'done': True})}\n\n"
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ============================================================================
# NEW ADMIN PANEL ENDPOINTS
# ============================================================================

@app.get("/api/models")
async def list_models():
    """
    List all available models from models.json.

    Returns model configurations with their aliases and recommended settings.
    """
    try:
        models = model_manager.list_available_models(enabled_only=False)
        defaults = model_manager.config.get("defaults", {})
        scheduler_aliases = model_manager.config.get("scheduler_aliases", {})

        return {
            "models": models,
            "defaults": defaults,
            "scheduler_aliases": scheduler_aliases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")


@app.get("/api/experiments")
async def list_experiments():
    """
    List all experiment directories with basic metadata.

    Returns a list of experiments with image counts and creation times.
    """
    try:
        experiments = []

        if not RESULTS_DIR.exists():
            return {"experiments": []}

        for exp_dir in RESULTS_DIR.iterdir():
            if not exp_dir.is_dir():
                continue

            # Count images
            images = list(exp_dir.glob("*.png"))
            results_file = exp_dir / "results.json"

            # Get creation time
            created_at = exp_dir.stat().st_ctime

            # Get stages from filenames
            stages = set()
            for img in images:
                parts = img.stem.split("_")
                if len(parts) >= 1:
                    stages.add(parts[0])

            experiments.append({
                "experiment_id": exp_dir.name,
                "created_at": created_at,
                "image_count": len(images),
                "stages": list(stages),
                "has_results": results_file.exists(),
                "latest_image": images[0].name if images else None
            })

        # Sort by creation time (newest first)
        experiments.sort(key=lambda x: x["created_at"], reverse=True)

        return {"experiments": experiments}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing experiments: {str(e)}")


@app.get("/api/experiments/{experiment_id}")
async def get_experiment(experiment_id: str):
    """
    Get detailed information about a specific experiment.

    Returns all images, metadata, and results for the experiment.
    """
    try:
        exp_dir = RESULTS_DIR / experiment_id

        if not exp_dir.exists():
            raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found")

        # Get all images
        images = []
        for img_path in sorted(exp_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True):
            stat = img_path.stat()
            images.append({
                "filename": img_path.name,
                "path": f"/api/experiments/{experiment_id}/images/{img_path.name}",
                "size_bytes": stat.st_size,
                "created_at": stat.st_mtime
            })

        # Load results.json if exists
        results_file = exp_dir / "results.json"
        results = []
        if results_file.exists():
            with open(results_file, "r") as f:
                results = json.load(f)

        return {
            "experiment_id": experiment_id,
            "images": images,
            "results": results,
            "stats": {
                "total_images": len(images),
                "successful": len([r for r in results if r.get("ok")]),
                "failed": len([r for r in results if not r.get("ok")])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting experiment: {str(e)}")


@app.get("/api/experiments/{experiment_id}/images/{filename}")
async def serve_image(experiment_id: str, filename: str):
    """
    Serve a generated image file.

    Returns the image file for display in the admin panel.
    """
    try:
        image_path = RESULTS_DIR / experiment_id / filename

        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")

        if not image_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            raise HTTPException(status_code=400, detail="Invalid image file")

        return FileResponse(image_path, media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")


@app.delete("/api/experiments/{experiment_id}")
async def delete_experiment(experiment_id: str):
    """
    Delete an experiment and all its images.

    Removes the experiment directory and all contents.
    """
    try:
        exp_dir = RESULTS_DIR / experiment_id

        if not exp_dir.exists():
            raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found")

        # Delete all files in directory
        import shutil
        shutil.rmtree(exp_dir)

        return {"ok": True, "message": f"Experiment '{experiment_id}' deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting experiment: {str(e)}")


async def process_batch_job(batch_id: str):
    """
    Background task to process a batch job.

    Executes all generation requests in the batch sequentially.
    """
    job = job_manager.get_job(batch_id)
    if not job:
        return

    for idx, item in enumerate(job.items):
        try:
            # Mark item as started
            job_manager.mark_item_started(batch_id, idx)

            # Create progress callback to update item progress
            def progress_callback(data: dict):
                progress = data.get("progress", 0)
                job_manager.update_item_progress(batch_id, idx, progress)

            # Create output directory
            output_dir = RESULTS_DIR / job.experiment_id
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate image with progress callback
            image_path, metadata = comfyui.generate_image(
                item.request,
                output_dir,
                progress_callback=progress_callback
            )

            # Mark as completed
            result = {
                "ok": True,
                "experiment_id": job.experiment_id,
                "stage": item.request.stage,
                "image_path": image_path,
                "metadata": metadata
            }
            job_manager.mark_item_completed(batch_id, idx, result)

        except Exception as e:
            # Mark as failed
            job_manager.mark_item_failed(batch_id, idx, str(e))


@app.post("/api/batch")
async def create_batch_job(
    request: BatchRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a batch of generation requests.

    Creates a batch job and processes it in the background.
    Returns a batch_id for tracking progress.
    """
    try:
        if not request.experiments:
            raise HTTPException(status_code=400, detail="No experiments provided")

        # Check ComfyUI availability
        if not comfyui.health_check():
            raise HTTPException(
                status_code=503,
                detail=f"ComfyUI is not available at {COMFYUI_URL}"
            )

        # Create batch job
        batch_id = job_manager.create_batch_job(request.experiment_id, request.experiments)

        # Start processing in background
        background_tasks.add_task(process_batch_job, batch_id)

        return {
            "batch_id": batch_id,
            "status": "queued",
            "total": len(request.experiments)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating batch job: {str(e)}")


@app.get("/api/batch/{batch_id}")
async def get_batch_status(batch_id: str):
    """
    Get the status and progress of a batch job.

    Returns current progress, completed items, and results.
    """
    status = job_manager.get_job_status(batch_id)

    if not status:
        raise HTTPException(status_code=404, detail=f"Batch job '{batch_id}' not found")

    return status


@app.get("/api/batch")
async def list_batch_jobs():
    """List all batch jobs."""
    return {"jobs": job_manager.list_jobs()}


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
