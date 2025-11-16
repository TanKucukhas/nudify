#!/usr/bin/env python3
"""
Simple API test script to verify backend functionality.
"""
import requests
import sys


def test_health(api_url: str) -> bool:
    """Test the /health endpoint."""
    print(f"Testing {api_url}/health ...")

    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        data = response.json()

        print(f"  Status: {data.get('status')}")
        print(f"  ComfyUI: {data.get('comfyui')}")

        return data.get('status') in ['healthy', 'degraded']

    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_root(api_url: str) -> bool:
    """Test the root endpoint."""
    print(f"\nTesting {api_url}/ ...")

    try:
        response = requests.get(api_url, timeout=5)
        data = response.json()

        print(f"  Name: {data.get('name')}")
        print(f"  Version: {data.get('version')}")

        return True

    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Run API tests."""
    api_url = "http://localhost:8000"

    print("=" * 60)
    print("Backend API Test")
    print("=" * 60)
    print()

    # Test root
    if not test_root(api_url):
        print("\n✗ Root endpoint test failed")
        print("\nMake sure the backend server is running:")
        print("  python -m backend.server")
        sys.exit(1)

    # Test health
    if not test_health(api_url):
        print("\n✗ Health endpoint test failed")
        sys.exit(1)

    print()
    print("=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Make sure ComfyUI is running at http://localhost:8188")
    print("  2. Run an experiment:")
    print("     python scripts/run_experiments.py --config configs/exp001_params.json")


if __name__ == "__main__":
    main()
