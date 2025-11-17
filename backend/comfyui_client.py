"""
ComfyUI API client for image generation.
"""
import json
import uuid
import time
import requests
import websocket
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from .models import GenerateRequest
from .model_manager import ModelManager


class ComfyUIClient:
    """Client for interacting with ComfyUI API."""

    def __init__(self, base_url: str = "http://localhost:8188"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        self.client_id = str(uuid.uuid4())
        self.model_manager = ModelManager(comfyui_url=base_url)
        self.ws = None
        self.ws_thread = None
        self.progress_data = {}
        self.prompt_outputs = {}

    def generate_image(
        self,
        request: GenerateRequest,
        output_dir: Path,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate an image using ComfyUI.

        Args:
            request: Generation request parameters
            output_dir: Directory to save output images
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (image_path, metadata)
        """
        # Connect to WebSocket for progress updates
        if progress_callback:
            self._connect_websocket(progress_callback)

        # Create workflow from request parameters
        workflow = self._create_workflow(request)

        # Submit workflow to ComfyUI
        prompt_id = self._queue_prompt(workflow)

        # Notify progress: prompt queued
        if progress_callback:
            progress_callback({
                "status": "queued",
                "message": "Workflow queued in ComfyUI",
                "progress": 0.0
            })

        # Wait for completion and get results
        output_images = self._wait_for_completion(prompt_id, progress_callback)

        # Disconnect WebSocket
        if self.ws:
            self._disconnect_websocket()

        # Save image to output directory
        image_path = self._save_image(output_images[0], output_dir, request)

        # Notify progress: complete
        if progress_callback:
            progress_callback({
                "status": "complete",
                "message": "Image saved successfully",
                "progress": 1.0,
                "image_path": str(image_path)
            })

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

    def _parse_scheduler(self, scheduler_str: str) -> tuple[str, str]:
        """
        Parse scheduler string into (sampler_name, scheduler).

        Examples:
            "DPM++ 2M Karras" -> ("dpmpp_2m", "karras")
            "euler" -> ("euler", "normal")
            "dpmpp_2m" -> ("dpmpp_2m", "normal")
        """
        # Mapping of common scheduler strings to (sampler, scheduler)
        scheduler_map = {
            "dpm++ 2m karras": ("dpmpp_2m", "karras"),
            "dpm++ 2m": ("dpmpp_2m", "normal"),
            "dpm++ sde karras": ("dpmpp_sde", "karras"),
            "dpm++ sde": ("dpmpp_sde", "normal"),
            "euler a": ("euler_ancestral", "normal"),
            "euler_a": ("euler_ancestral", "normal"),
        }

        # Normalize input
        normalized = scheduler_str.lower().strip()

        # Check if it's a known combined scheduler
        if normalized in scheduler_map:
            return scheduler_map[normalized]

        # Valid schedulers
        valid_schedulers = ["simple", "normal", "karras", "exponential", "sgm_uniform",
                          "ddim_uniform", "beta", "linear_quadratic", "kl_optimal"]

        # If it ends with a known scheduler name, split it
        for sched in valid_schedulers:
            if normalized.endswith(sched):
                # Extract sampler part
                sampler = normalized.replace(sched, "").strip()
                if sampler:
                    return (sampler, sched)

        # Default: assume it's just a sampler name
        return (scheduler_str, "normal")

    def _create_workflow(self, request: GenerateRequest) -> Dict[str, Any]:
        """
        Create a ComfyUI workflow from request parameters.

        Note: This is a simplified workflow structure. In practice, you would
        load a template workflow JSON and substitute the parameters.
        """
        # Generate random seed if not provided
        seed = request.seed if request.seed is not None else int(time.time())

        # Resolve model name using ModelManager
        try:
            ckpt_name = self.model_manager.resolve_model(request.model)
        except ValueError as e:
            raise ValueError(f"Model resolution failed: {e}")

        # Resolve scheduler alias if provided
        scheduler_str = request.extra.scheduler if request.extra and request.extra.scheduler else "euler"
        scheduler_str = self.model_manager.resolve_scheduler(scheduler_str)

        # Basic workflow structure
        # This should be customized based on your actual ComfyUI setup
        workflow = {
            "prompt": {
                # Load Checkpoint
                "1": {
                    "inputs": {
                        "ckpt_name": ckpt_name
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
                        "sampler_name": self._parse_scheduler(scheduler_str)[0],
                        "scheduler": self._parse_scheduler(scheduler_str)[1],
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

    def _wait_for_completion(
        self,
        prompt_id: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        timeout: int = 300
    ) -> list:
        """
        Wait for a prompt to complete and return the output images.

        Uses WebSocket events if available, falls back to polling.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if we received output via WebSocket
            if prompt_id in self.prompt_outputs:
                return self.prompt_outputs[prompt_id]

            # Fallback: Check history for completed prompt
            url = f"{self.base_url}/history/{prompt_id}"
            response = requests.get(url)

            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            if progress_callback:
                                progress_callback({
                                    "status": "saving",
                                    "message": "Downloading generated image",
                                    "progress": 0.95
                                })
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

    def _connect_websocket(self, progress_callback: Callable[[Dict[str, Any]], None]) -> None:
        """Connect to ComfyUI WebSocket for real-time updates."""
        try:
            ws_url = f"{self.ws_url}/ws?clientId={self.client_id}"

            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")

                    if msg_type == "execution_start":
                        progress_callback({
                            "status": "starting",
                            "message": "Starting execution",
                            "progress": 0.05
                        })

                    elif msg_type == "executing":
                        node_id = data.get("data", {}).get("node")
                        if node_id:
                            progress_callback({
                                "status": "executing",
                                "message": f"Executing node {node_id}",
                                "progress": 0.1
                            })

                    elif msg_type == "progress":
                        # Progress event: {type: "progress", data: {value: 5, max: 20}}
                        progress_data = data.get("data", {})
                        value = progress_data.get("value", 0)
                        max_val = progress_data.get("max", 1)

                        if max_val > 0:
                            # Map to 10% - 90% range (0-10% is queue/start, 90-100% is saving)
                            progress_pct = 0.1 + (value / max_val) * 0.8

                            progress_callback({
                                "status": "generating",
                                "message": f"Generating step {value}/{max_val}",
                                "progress": progress_pct,
                                "step": value,
                                "total_steps": max_val
                            })

                    elif msg_type == "executed":
                        # Execution complete, check for output
                        prompt_id = data.get("data", {}).get("prompt_id")
                        output = data.get("data", {}).get("output", {})

                        if prompt_id and output:
                            for node_id, node_output in output.items():
                                if "images" in node_output:
                                    self.prompt_outputs[prompt_id] = node_output["images"]

                        progress_callback({
                            "status": "executed",
                            "message": "Execution complete",
                            "progress": 0.9
                        })

                except Exception as e:
                    print(f"Error processing WebSocket message: {e}")

            def on_error(ws, error):
                print(f"WebSocket error: {error}")

            def on_close(ws, close_status_code, close_msg):
                pass

            def on_open(ws):
                progress_callback({
                    "status": "connected",
                    "message": "Connected to ComfyUI",
                    "progress": 0.0
                })

            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )

            # Run WebSocket in a separate thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.ws_thread.start()

            # Give it a moment to connect
            time.sleep(0.5)

        except Exception as e:
            print(f"Failed to connect WebSocket: {e}")

    def _disconnect_websocket(self) -> None:
        """Disconnect from ComfyUI WebSocket."""
        if self.ws:
            self.ws.close()
            self.ws = None
        if self.ws_thread:
            self.ws_thread = None

    def health_check(self) -> bool:
        """Check if ComfyUI is accessible."""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
