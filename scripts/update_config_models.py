#!/usr/bin/env python3
"""
Update experiment configs to use model aliases.

This script helps convert existing experiment configs that use direct
checkpoint filenames to use model aliases from models.json.
"""
import json
import sys
from pathlib import Path
import click

sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.model_manager import ModelManager


def get_alias_for_checkpoint(model_manager: ModelManager, checkpoint: str) -> str:
    """
    Find the alias for a given checkpoint filename.

    Returns the alias if found, otherwise returns the checkpoint name as-is.
    """
    models = model_manager.config.get("models", {})

    for alias, config in models.items():
        if config.get("checkpoint_file") == checkpoint:
            return alias

    # No alias found, return original
    return checkpoint


@click.command()
@click.argument("config_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file (default: overwrite input file)"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show changes without writing to file"
)
@click.option(
    "--models-config",
    default="configs/models.json",
    help="Path to models.json"
)
def main(config_file: Path, output: Path, dry_run: bool, models_config: str):
    """
    Update experiment config to use model aliases.

    Example:
        python scripts/update_config_models.py configs/exp001_params.json
        python scripts/update_config_models.py configs/exp001_params.json --dry-run
    """
    print(f"Reading config: {config_file}")

    # Load experiment config
    with open(config_file, "r") as f:
        config = json.load(f)

    # Load model manager
    try:
        model_manager = ModelManager(config_path=models_config)
    except FileNotFoundError:
        print(f"Error: {models_config} not found")
        sys.exit(1)

    # Track changes
    changes = []

    # Update experiments
    if "experiments" in config:
        for idx, exp in enumerate(config["experiments"]):
            if "model" in exp:
                old_model = exp["model"]
                new_model = get_alias_for_checkpoint(model_manager, old_model)

                if old_model != new_model:
                    changes.append((f"experiments[{idx}].model", old_model, new_model))
                    exp["model"] = new_model

    # Report changes
    if not changes:
        print("✓ No changes needed (models already use aliases)")
        return

    print(f"\nFound {len(changes)} changes:")
    for path, old, new in changes:
        print(f"  {path}:")
        print(f"    {old} → {new}")

    if dry_run:
        print("\n(Dry run - no files were modified)")
        return

    # Write output
    output_file = output if output else config_file

    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✓ Updated config saved to: {output_file}")


if __name__ == "__main__":
    main()
