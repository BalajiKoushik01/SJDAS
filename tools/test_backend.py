import base64
import json
import os
import subprocess
import sys
import time

import requests


def test_backend():
    print("🚀 Testing Backend API...")

    # Define payload
    payload = {
        "design_type": "border",
        "style": "traditional",
        "colors": ["red", "gold"],
        "motifs": ["geometric"],
        "weave": "jeri"
    }

    try:
        # Test Root
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Root Endpoint: OK")
        else:
            print(f"❌ Root Endpoint Failed: {response.status_code}")
            return False

        # Test Procedural Gen
        print("Testing Procedural Generation...")
        start = time.time()
        response = requests.post(
            "http://localhost:8000/generate/procedural",
            json=payload)
        duration = time.time() - start

        if response.status_code == 200:
            data = response.json()
            if "image" in data and len(data["image"]) > 100:
                print(f"✅ Procedural Gen: OK ({duration:.2f}s)")
            else:
                print("❌ Procedural Gen: Invalid response format")
                return False
        else:
            print(f"❌ Procedural Gen Failed: {response.status_code}")
            print(response.text)
            return False

        print("\n✨ All Backend Tests Passed!")
        return True

    except requests.exceptions.ConnectionError:
        print("❌ Connection Refused. Is the server running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    # Start server in background
    print("Starting server...")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server_process = subprocess.Popen(
        [sys.executable, "backend/main.py"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for startup
    time.sleep(5)

    success = test_backend()

    # Kill server
    server_process.kill()

    sys.exit(0 if success else 1)
