"""
ComfyUI API client for image generation.
"""
import json
import uuid
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from .models import GenerateRequest


class ComfyUIClient:
    """Client for interacting with ComfyUI API."""

    def __init__(self, base_url: str = "http://localhost:8188"):
        self.base_url = base_url
        self.client_id = str(uuid.uuid4())

    def generate_image(
        self,
        request: GenerateRequest,
        output_dir: Path
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate an image using ComfyUI.

        Args:
            request: Generation request parameters
            output_dir: Directory to save output images

        Returns:
            Tuple of (image_path, metadata)
        """
        # Create workflow from request parameters
        workflow = self._create_workflow(request)

        # Submit workflow to ComfyUI
        prompt_id = self._queue_prompt(workflow)

        # Wait for completion and get results
        output_images = self._wait_for_completion(prompt_id)

        # Save image to output directory
        image_path = self._save_image(output_images[0], output_dir, request)

        # Build metadata
        metadata = {
            "seed": request.seed or 0,
            "model": request.model,
            "steps": request.steps,
            "cfg_scale": request.cfg_scale,
            "width": request.width,
            "height": request.height,
            "denoise": request.extra.denoise if request.extra else None,
            "scheduler": request.extra.scheduler if request.extra else None,
        }

        return str(image_path), metadata

    def _create_workflow(self, request: GenerateRequest) -> Dict[str, Any]:
        """
        Create a ComfyUI workflow from request parameters.

        Note: This is a simplified workflow structure. In practice, you would
        load a template workflow JSON and substitute the parameters.
        """
        # Generate random seed if not provided
        seed = request.seed if request.seed is not None else int(time.time())

        # Map model names to checkpoint files
        # Update these to match your actual model filenames in ComfyUI
        model_map = {
            "sd15": "sd_v1-5.safetensors",
            "sdxl_base": "sd_xl_base_1.0.safetensors",
            "sdxl_lightning": "sdxl_lightning_4step.safetensors",
            "flux_schnell": "flux1-schnell.safetensors",
            "flux_dev": "flux1-dev.safetensors",
        }

        # Basic workflow structure
        # This should be customized based on your actual ComfyUI setup
        workflow = {
            "prompt": {
                # Load Checkpoint
                "1": {
                    "inputs": {
                        "ckpt_name": model_map.get(request.model, "sdxl_lightning.safetensors")
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                # Positive Prompt
                "2": {
                    "inputs": {
                        "text": request.prompt,
                        "clip": ["1", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                # Negative Prompt
                "3": {
                    "inputs": {
                        "text": request.negative_prompt,
                        "clip": ["1", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                # Empty Latent Image
                "4": {
                    "inputs": {
                        "width": request.width,
                        "height": request.height,
                        "batch_size": 1
                    },
                    "class_type": "EmptyLatentImage"
                },
                # KSampler
                "5": {
                    "inputs": {
                        "seed": seed,
                        "steps": request.steps,
                        "cfg": request.cfg_scale,
                        "sampler_name": request.extra.scheduler if request.extra else "euler",
                        "scheduler": "normal",
                        "denoise": request.extra.denoise if (request.extra and request.input_image) else 1.0,
                        "model": ["1", 0],
                        "positive": ["2", 0],
                        "negative": ["3", 0],
                        "latent_image": ["4", 0]
                    },
                    "class_type": "KSampler"
                },
                # VAE Decode
                "6": {
                    "inputs": {
                        "samples": ["5", 0],
                        "vae": ["1", 2]
                    },
                    "class_type": "VAEDecode"
                },
                # Save Image
                "7": {
                    "inputs": {
                        "filename_prefix": f"{request.experiment_id}_{request.stage}",
                        "images": ["6", 0]
                    },
                    "class_type": "SaveImage"
                }
            },
            "client_id": self.client_id
        }

        return workflow

    def _queue_prompt(self, workflow: Dict[str, Any]) -> str:
        """Queue a prompt in ComfyUI and return the prompt ID."""
        url = f"{self.base_url}/prompt"
        response = requests.post(url, json=workflow)
        response.raise_for_status()
        result = response.json()
        return result["prompt_id"]

    def _wait_for_completion(self, prompt_id: str, timeout: int = 300) -> list:
        """
        Wait for a prompt to complete and return the output images.

        This is a simplified implementation. A production version would use
        WebSocket connections for real-time updates.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check history for completed prompt
            url = f"{self.base_url}/history/{prompt_id}"
            response = requests.get(url)

            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            return node_output["images"]

            time.sleep(1)

        raise TimeoutError(f"Prompt {prompt_id} did not complete within {timeout}s")

    def _save_image(
        self,
        image_info: Dict[str, Any],
        output_dir: Path,
        request: GenerateRequest
    ) -> Path:
        """Download and save an image from ComfyUI."""
        # Get image from ComfyUI
        filename = image_info["filename"]
        subfolder = image_info.get("subfolder", "")
        image_type = image_info.get("type", "output")

        url = f"{self.base_url}/view"
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": image_type
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        # Save to output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create unique filename
        timestamp = int(time.time())
        seed_str = f"_{request.seed}" if request.seed else ""
        output_filename = f"{request.stage}_{timestamp}{seed_str}.png"
        output_path = output_dir / output_filename

        output_path.write_bytes(response.content)

        return output_path

    def health_check(self) -> bool:
        """Check if ComfyUI is accessible."""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
