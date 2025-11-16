#!/usr/bin/env python3
"""
Image evaluation script using Claude.

Uses Claude's vision capabilities to evaluate generated images
according to predefined criteria.
"""
import json
import sys
import base64
from pathlib import Path
from typing import List, Dict, Any
import click
import os


def load_prompt_template(template_path: Path) -> str:
    """Load the evaluation prompt template."""
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")

    with open(template_path, "r") as f:
        return f.read()


def find_images(image_dir: Path) -> List[Path]:
    """Find all images in the directory."""
    image_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    images = []

    for ext in image_extensions:
        images.extend(image_dir.glob(f"*{ext}"))

    return sorted(images)


def encode_image(image_path: Path) -> str:
    """Encode image to base64 for Claude API."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def evaluate_image_with_claude(
    image_path: Path,
    prompt_template: str,
    api_key: str
) -> Dict[str, Any]:
    """
    Evaluate an image using Claude API.

    Note: This is a placeholder implementation. In production, you would
    use the actual Claude API or CLI.

    For now, this returns a mock evaluation structure.
    """
    # TODO: Implement actual Claude API call
    # This would use the Anthropic Python SDK:
    #
    # import anthropic
    # client = anthropic.Anthropic(api_key=api_key)
    #
    # image_data = encode_image(image_path)
    #
    # message = client.messages.create(
    #     model="claude-3-5-sonnet-20241022",
    #     max_tokens=1024,
    #     messages=[{
    #         "role": "user",
    #         "content": [
    #             {
    #                 "type": "image",
    #                 "source": {
    #                     "type": "base64",
    #                     "media_type": "image/png",
    #                     "data": image_data,
    #                 },
    #             },
    #             {
    #                 "type": "text",
    #                 "text": prompt_template
    #             }
    #         ],
    #     }],
    # )
    #
    # # Parse JSON response from Claude
    # response_text = message.content[0].text
    # # Extract JSON from markdown code blocks if present
    # evaluation = parse_json_response(response_text)

    # Mock evaluation for now
    print(f"   [Mock] Would evaluate: {image_path.name}")

    return {
        "file": str(image_path.name),
        "pose": 7,
        "anatomy": 7,
        "lighting": 6,
        "realism": 7,
        "notes": "Mock evaluation - implement Claude API integration to get real scores"
    }


def parse_json_response(response: str) -> Dict[str, Any]:
    """
    Parse JSON from Claude's response, handling markdown code blocks.
    """
    # Remove markdown code blocks if present
    if "```json" in response:
        start = response.find("```json") + 7
        end = response.find("```", start)
        response = response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        response = response[start:end].strip()

    return json.loads(response)


def save_evaluations(evaluations: List[Dict[str, Any]], output_path: Path) -> None:
    """Save evaluations to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(evaluations, f, indent=2)

    print(f"\n✓ Evaluations saved to {output_path}")


@click.command()
@click.option(
    "--images",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Directory containing images to evaluate"
)
@click.option(
    "--out",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="Output JSON file for evaluations"
)
@click.option(
    "--prompt",
    "-p",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to evaluation prompt template (default: claude/prompts/evaluate_images.md)"
)
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Maximum number of images to evaluate"
)
def main(
    images: Path,
    out: Path,
    prompt: Path,
    api_key: str,
    limit: int
):
    """
    Evaluate generated images using Claude's vision capabilities.

    Example:
        export ANTHROPIC_API_KEY=your_key_here
        python scripts/eval_with_claude.py \\
            --images results_dev/exp001 \\
            --out results_dev/exp001_eval.json
    """
    print("=" * 60)
    print("AI Image Generation Lab - Claude Evaluation")
    print("=" * 60)

    # Load prompt template
    if prompt is None:
        prompt = Path("claude/prompts/evaluate_images.md")

    print(f"\n📄 Loading prompt template from {prompt}")
    prompt_template = load_prompt_template(prompt)

    # Find images
    print(f"\n🔍 Finding images in {images}")
    image_files = find_images(images)

    if not image_files:
        print(f"   ✗ No images found in {images}")
        sys.exit(1)

    print(f"   Found {len(image_files)} images")

    # Apply limit if specified
    if limit:
        image_files = image_files[:limit]
        print(f"   Limited to {limit} images")

    # Check API key
    if not api_key:
        print("\n⚠ Warning: No API key provided")
        print("   Set ANTHROPIC_API_KEY environment variable or use --api-key")
        print("   Running in mock mode...")
        mock_mode = True
    else:
        print("\n✓ API key found")
        mock_mode = False

    # Evaluate images
    print(f"\n🤖 Evaluating {len(image_files)} images...")
    print()

    evaluations = []

    for idx, image_path in enumerate(image_files, 1):
        print(f"[{idx}/{len(image_files)}] {image_path.name}")

        try:
            evaluation = evaluate_image_with_claude(
                image_path,
                prompt_template,
                api_key
            )

            evaluations.append(evaluation)

            # Print scores
            print(f"   Pose: {evaluation['pose']}/10")
            print(f"   Anatomy: {evaluation['anatomy']}/10")
            print(f"   Lighting: {evaluation['lighting']}/10")
            print(f"   Realism: {evaluation['realism']}/10")

        except Exception as e:
            print(f"   ✗ Error: {e}")
            evaluations.append({
                "file": str(image_path.name),
                "error": str(e)
            })

    # Save evaluations
    save_evaluations(evaluations, out)

    # Summary statistics
    valid_evals = [e for e in evaluations if "error" not in e]

    if valid_evals:
        print()
        print("=" * 60)
        print("Summary Statistics")
        print("=" * 60)

        avg_pose = sum(e["pose"] for e in valid_evals) / len(valid_evals)
        avg_anatomy = sum(e["anatomy"] for e in valid_evals) / len(valid_evals)
        avg_lighting = sum(e["lighting"] for e in valid_evals) / len(valid_evals)
        avg_realism = sum(e["realism"] for e in valid_evals) / len(valid_evals)

        print(f"Average Pose:     {avg_pose:.1f}/10")
        print(f"Average Anatomy:  {avg_anatomy:.1f}/10")
        print(f"Average Lighting: {avg_lighting:.1f}/10")
        print(f"Average Realism:  {avg_realism:.1f}/10")

        if mock_mode:
            print("\n⚠ Note: These are mock scores. Set ANTHROPIC_API_KEY for real evaluations.")


if __name__ == "__main__":
    main()
