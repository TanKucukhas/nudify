#!/usr/bin/env python3
"""
Experiment runner script.

Reads experiment configuration files and executes image generation
requests against the backend API.
"""
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import click
import requests
from jsonschema import validate, ValidationError


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load and validate experiment configuration."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = json.load(f)

    return config


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load JSON schema for validation."""
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "r") as f:
        schema = json.load(f)

    return schema


def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Validate configuration against schema."""
    try:
        validate(instance=config, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Configuration validation failed: {e.message}")


def run_experiment(
    experiment: Dict[str, Any],
    experiment_id: str,
    api_url: str
) -> Dict[str, Any]:
    """
    Run a single experiment by calling the backend API.

    Args:
        experiment: Experiment parameters
        experiment_id: Experiment batch ID
        api_url: Backend API URL

    Returns:
        Response from the API
    """
    # Add experiment_id to the request
    request_data = {
        "experiment_id": experiment_id,
        **experiment
    }

    # Call the API
    response = requests.post(
        f"{api_url}/generate",
        json=request_data,
        timeout=300  # 5 minute timeout
    )

    response.raise_for_status()
    return response.json()


def save_results(results: List[Dict[str, Any]], output_path: Path) -> None:
    """Save experiment results to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to {output_path}")


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to experiment configuration JSON file"
)
@click.option(
    "--out",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory for results (default: results_dev/<experiment_id>)"
)
@click.option(
    "--api-url",
    default="http://localhost:8001",
    help="Backend API URL (default: http://localhost:8001)"
)
@click.option(
    "--schema",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to JSON schema for validation (default: configs/schema.json)"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Validate config without running experiments"
)
def main(
    config: Path,
    out: Path,
    api_url: str,
    schema: Path,
    dry_run: bool
):
    """
    Run image generation experiments from a configuration file.

    Example:
        python scripts/run_experiments.py --config configs/exp001_params.json
    """
    print("=" * 60)
    print("AI Image Generation Lab - Experiment Runner")
    print("=" * 60)

    # Load configuration
    print(f"\n📄 Loading configuration from {config}")
    config_data = load_config(config)

    experiment_id = config_data.get("experiment_id")
    experiments = config_data.get("experiments", [])

    print(f"   Experiment ID: {experiment_id}")
    print(f"   Number of experiments: {len(experiments)}")

    # Validate configuration
    if schema is None:
        schema = Path("configs/schema.json")

    if schema.exists():
        print(f"\n✓ Validating configuration against {schema}")
        schema_data = load_schema(schema)
        try:
            validate_config(config_data, schema_data)
            print("   Configuration is valid!")
        except ValueError as e:
            print(f"   ✗ {e}")
            sys.exit(1)
    else:
        print(f"\n⚠ Schema not found at {schema}, skipping validation")

    if dry_run:
        print("\n✓ Dry run complete. Configuration is valid.")
        return

    # Check API health
    print(f"\n🔍 Checking API health at {api_url}")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        health_data = response.json()
        print(f"   Status: {health_data.get('status')}")
        print(f"   ComfyUI: {health_data.get('comfyui')}")

        if health_data.get("status") != "healthy":
            print("\n⚠ Warning: API is not fully healthy, some requests may fail")

    except Exception as e:
        print(f"   ✗ Failed to connect to API: {e}")
        sys.exit(1)

    # Determine output directory
    if out is None:
        out = Path("results_dev") / experiment_id

    print(f"\n📁 Output directory: {out}")
    out.mkdir(parents=True, exist_ok=True)

    # Run experiments
    print(f"\n🚀 Running {len(experiments)} experiments...")
    print()

    results = []
    successful = 0
    failed = 0

    for idx, experiment in enumerate(experiments, 1):
        stage = experiment.get("stage", "unknown")
        seed = experiment.get("seed", "random")

        print(f"[{idx}/{len(experiments)}] Stage: {stage}, Seed: {seed}")

        try:
            start_time = time.time()
            result = run_experiment(experiment, experiment_id, api_url)
            elapsed = time.time() - start_time

            results.append(result)
            successful += 1

            image_path = result.get("image_path", "unknown")
            print(f"   ✓ Success ({elapsed:.1f}s): {image_path}")

        except requests.exceptions.HTTPError as e:
            failed += 1
            error_msg = str(e)

            try:
                error_detail = e.response.json().get("detail", str(e))
                error_msg = error_detail
            except:
                pass

            results.append({
                "ok": False,
                "experiment_id": experiment_id,
                "stage": stage,
                "error": error_msg
            })

            print(f"   ✗ Failed: {error_msg}")

        except Exception as e:
            failed += 1
            results.append({
                "ok": False,
                "experiment_id": experiment_id,
                "stage": stage,
                "error": str(e)
            })

            print(f"   ✗ Error: {e}")

        # Small delay between requests
        if idx < len(experiments):
            time.sleep(0.5)

    # Save results
    results_file = out / "results.json"
    save_results(results, results_file)

    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total experiments: {len(experiments)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Results saved to: {results_file}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
