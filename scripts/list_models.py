#!/usr/bin/env python3
"""
List available models from ComfyUI and compare with configuration.

This script helps you verify which models are actually available in ComfyUI
and which ones are configured in models.json.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.model_manager import ModelManager
import click


@click.command()
@click.option(
    "--comfyui-url",
    default="http://localhost:8000",
    help="ComfyUI URL (default: http://localhost:8000)"
)
@click.option(
    "--config",
    default="configs/models.json",
    help="Path to models.json (default: configs/models.json)"
)
@click.option(
    "--show-all",
    is_flag=True,
    help="Show all models including disabled ones"
)
def main(comfyui_url: str, config: str, show_all: bool):
    """
    List models from ComfyUI and compare with configuration.
    """
    print("=" * 70)
    print("Model Configuration Inspector")
    print("=" * 70)
    print()

    # Initialize model manager
    try:
        model_manager = ModelManager(config_path=config, comfyui_url=comfyui_url)
        print(f"✓ Loaded configuration from: {config}")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

    print(f"✓ ComfyUI URL: {comfyui_url}")
    print()

    # Fetch available models from ComfyUI
    print("Fetching models from ComfyUI...")
    available = model_manager.get_available_models_from_comfyui()

    if not available:
        print("⚠ Warning: Could not fetch models from ComfyUI")
        print("  Make sure ComfyUI is running at", comfyui_url)
        print()
    else:
        print(f"✓ Found {len(available)} models in ComfyUI")
        print()

    # List configured models
    print("-" * 70)
    print("CONFIGURED MODELS")
    print("-" * 70)
    print()

    configured = model_manager.list_available_models(enabled_only=not show_all)

    if not configured:
        print("No models configured!")
    else:
        for model in configured:
            status = "✓" if model["enabled"] else "✗"
            available_status = "✓" if model["checkpoint_file"] in available else "✗"

            print(f"{status} {model['alias']:<20} [{model['type']}]")
            print(f"  Checkpoint: {model['checkpoint_file']}")
            print(f"  Available in ComfyUI: {available_status}")
            print(f"  Description: {model['description']}")
            print()

    # List available models not in config
    print("-" * 70)
    print("MODELS IN COMFYUI (Not in Config)")
    print("-" * 70)
    print()

    configured_checkpoints = {m["checkpoint_file"] for m in configured}
    unconfigured = [m for m in available if m not in configured_checkpoints]

    if unconfigured:
        for model_file in unconfigured:
            print(f"  • {model_file}")
        print()
        print("💡 Tip: Add these to configs/models.json if you want to use them")
    else:
        print("  (All ComfyUI models are configured)")

    print()
    print("-" * 70)
    print("RECOMMENDED USAGE")
    print("-" * 70)
    print()
    print("In your experiment configs, use model aliases like:")
    print()
    for model in configured[:3]:  # Show first 3
        if model["enabled"]:
            print(f'  "model": "{model["alias"]}"  // {model["description"][:50]}')
    print()


if __name__ == "__main__":
    main()
