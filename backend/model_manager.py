"""
Model management and configuration loader.

This module handles loading model configurations from the central models.json file
and provides utilities for model resolution and validation.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests


class ModelManager:
    """Manages model configurations and provides model resolution."""

    def __init__(self, config_path: str = "configs/models.json", comfyui_url: str = "http://localhost:8000"):
        """
        Initialize the model manager.

        Args:
            config_path: Path to the models.json configuration file
            comfyui_url: URL of the ComfyUI instance
        """
        self.config_path = Path(config_path)
        self.comfyui_url = comfyui_url
        self.config = self._load_config()
        self._available_models_cache = None

    def _load_config(self) -> Dict[str, Any]:
        """Load the model configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Model configuration not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            return json.load(f)

    def get_available_models_from_comfyui(self) -> List[str]:
        """
        Fetch the list of available checkpoint models from ComfyUI.

        Returns:
            List of available checkpoint filenames
        """
        try:
            response = requests.get(f"{self.comfyui_url}/object_info/CheckpointLoaderSimple", timeout=5)
            response.raise_for_status()
            data = response.json()

            # Extract model list from the response
            models = data.get("input", {}).get("required", {}).get("ckpt_name", [[]])[0]
            self._available_models_cache = models
            return models

        except Exception as e:
            print(f"Warning: Could not fetch models from ComfyUI: {e}")
            return []

    def resolve_model(self, model_name: str) -> str:
        """
        Resolve a model alias to its actual checkpoint filename.

        Args:
            model_name: Model name or alias (e.g., "sdxl_base", "sd_xl_base_1.0.safetensors")

        Returns:
            The actual checkpoint filename to use

        Raises:
            ValueError: If the model is not found or not enabled
        """
        models = self.config.get("models", {})

        # Check if it's a direct alias
        if model_name in models:
            model_config = models[model_name]

            # Check if model is enabled (default to True if not specified)
            if not model_config.get("enabled", True):
                raise ValueError(
                    f"Model '{model_name}' is disabled. "
                    f"Notes: {model_config.get('notes', 'No notes available')}"
                )

            return model_config["checkpoint_file"]

        # If it already looks like a checkpoint filename, use it directly
        if model_name.endswith(".safetensors") or model_name.endswith(".ckpt"):
            return model_name

        # Try adding .safetensors extension
        if f"{model_name}.safetensors" in [m.get("checkpoint_file") for m in models.values()]:
            return f"{model_name}.safetensors"

        # Fallback: use the model name as-is and let ComfyUI validate it
        print(f"Warning: Model '{model_name}' not found in config, using as-is")
        return model_name

    def validate_model(self, model_name: str) -> bool:
        """
        Validate that a model exists in ComfyUI.

        Args:
            model_name: Model name or alias

        Returns:
            True if the model is available, False otherwise
        """
        checkpoint_file = self.resolve_model(model_name)
        available = self.get_available_models_from_comfyui()

        return checkpoint_file in available

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the full configuration for a model.

        Args:
            model_name: Model name or alias

        Returns:
            Model configuration dict or None if not found
        """
        models = self.config.get("models", {})

        if model_name in models:
            return models[model_name]

        return None

    def get_recommended_settings(self, model_name: str) -> Dict[str, Any]:
        """
        Get recommended settings for a model.

        Args:
            model_name: Model name or alias

        Returns:
            Dict with recommended settings, or default settings if model not found
        """
        model_config = self.get_model_config(model_name)

        if model_config and "recommended_settings" in model_config:
            return model_config["recommended_settings"]

        # Return defaults
        return self.config.get("defaults", {})

    def list_available_models(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """
        List all configured models.

        Args:
            enabled_only: If True, only return enabled models

        Returns:
            List of model info dicts
        """
        models = self.config.get("models", {})
        result = []

        for alias, config in models.items():
            if enabled_only and not config.get("enabled", True):
                continue

            result.append({
                "alias": alias,
                "checkpoint_file": config["checkpoint_file"],
                "type": config.get("type", "unknown"),
                "description": config.get("description", ""),
                "enabled": config.get("enabled", True)
            })

        return result

    def resolve_scheduler(self, scheduler_name: str) -> str:
        """
        Resolve scheduler aliases.

        Args:
            scheduler_name: Scheduler name or alias

        Returns:
            Resolved scheduler name
        """
        aliases = self.config.get("scheduler_aliases", {})
        return aliases.get(scheduler_name, scheduler_name)
