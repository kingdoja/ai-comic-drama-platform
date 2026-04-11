"""
Manual verification script for Rerun API endpoints.

This script verifies that the Rerun API endpoints are correctly implemented
without requiring the full test infrastructure.

Run this after starting the API server to verify the endpoints work.
"""

import requests
from uuid import uuid4

# Base URL for the API
BASE_URL = "http://localhost:8000/api"


def test_rerun_workflow():
    """Test POST /episodes/{episode_id}/rerun"""
    episode_id = uuid4()
    
    payload = {
        "from_stage": "script",
        "reason": "Need to adjust dialogue"
    }
    
    response = requests.post(
        f"{BASE_URL}/episodes/{episode_id}/rerun",
        json=payload
    )
    
    print(f"POST /episodes/{episode_id}/rerun")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_rerun_shots():
    """Test POST /episodes/{episode_id}/rerun-shots"""
    episode_id = uuid4()
    shot_id1 = uuid4()
    shot_id2 = uuid4()
    
    payload = {
        "shot_ids": [str(shot_id1), str(shot_id2)],
        "stage_type": "image_render"
    }
    
    response = requests.post(
        f"{BASE_URL}/episodes/{episode_id}/rerun-shots",
        json=payload
    )
    
    print(f"POST /episodes/{episode_id}/rerun-shots")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_get_rerun_history():
    """Test GET /episodes/{episode_id}/rerun-history"""
    episode_id = uuid4()
    
    response = requests.get(
        f"{BASE_URL}/episodes/{episode_id}/rerun-history"
    )
    
    print(f"GET /episodes/{episode_id}/rerun-history")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Rerun API Manual Verification")
    print("=" * 60)
    print()
    print("Note: This script expects the API server to be running.")
    print("Start the server with: uvicorn app.main:app --reload")
    print()
    print("=" * 60)
    print()
    
    try:
        # Test workflow rerun endpoint
        test_rerun_workflow()
        
        # Test shot rerun endpoint
        test_rerun_shots()
        
        # Test rerun history endpoint
        test_get_rerun_history()
        
        print("=" * 60)
        print("All manual tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Please start the server with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"ERROR: {e}")
