"""
Data models for the image generation API.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ExtraParams(BaseModel):
    """Additional model-specific parameters."""
    denoise: Optional[float] = Field(default=0.75, ge=0.0, le=1.0)
    scheduler: Optional[str] = Field(
        default="euler",
        description="Sampler/scheduler name (e.g., 'euler', 'DPM++ 2M Karras', 'dpmpp_2m')"
    )
    clip_skip: Optional[int] = Field(default=0, ge=0, le=12)

    class Config:
        extra = "allow"  # Allow additional parameters


class GenerateRequest(BaseModel):
    """Request model for image generation."""
    experiment_id: str = Field(..., description="Experiment identifier", min_length=1)
    stage: str = Field(..., description="Pipeline stage (custom stages allowed)", min_length=1)
    prompt: str = Field(..., min_length=1, description="Positive prompt")
    negative_prompt: str = Field(default="", description="Negative prompt")
    seed: Optional[int] = Field(default=None, ge=0, le=4294967295, description="Random seed")
    width: int = Field(default=768, ge=64, le=2048, description="Image width")
    height: int = Field(default=512, ge=64, le=2048, description="Image height")
    steps: int = Field(default=20, ge=1, le=150, description="Sampling steps")
    cfg_scale: float = Field(default=7.0, ge=1.0, le=30.0, description="CFG scale")
    model: str = Field(
        ..., description="Model identifier (any ComfyUI-compatible model name)", min_length=1
    )
    input_image: Optional[str] = Field(default=None, description="Input image path for img2img")
    extra: Optional[ExtraParams] = Field(default_factory=ExtraParams, description="Additional parameters")


class ImageMetadata(BaseModel):
    """Metadata about generated image."""
    seed: int
    model: str
    steps: int
    cfg_scale: float
    width: int
    height: int
    denoise: Optional[float] = None
    scheduler: Optional[str] = None


class GenerateResponse(BaseModel):
    """Response model for image generation."""
    ok: bool = Field(..., description="Success status")
    experiment_id: str = Field(..., description="Experiment identifier")
    stage: str = Field(..., description="Pipeline stage")
    image_path: str = Field(..., description="Path to generated image")
    metadata: ImageMetadata = Field(..., description="Generation metadata")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class BatchRequest(BaseModel):
    """Request model for batch generation."""
    experiment_id: str = Field(..., description="Experiment identifier for the batch")
    experiments: List[GenerateRequest] = Field(..., description="List of generation requests")
