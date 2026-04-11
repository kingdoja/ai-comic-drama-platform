"""
Simple standalone test for Review API

This script tests the Review API endpoints without requiring the full test infrastructure.
"""

import sys
from uuid import uuid4

# Test imports
try:
    from app.schemas.review import (
        ReviewSubmitRequest,
        ReviewDecisionResponse,
        ReviewHistoryResponse,
        ReviewHistoryItem,
    )
    print("✓ Review schemas imported successfully")
except ImportError as e:
    print(f"✗ Failed to import review schemas: {e}")
    sys.exit(1)

# Test schema validation
try:
    # Test ReviewSubmitRequest
    request = ReviewSubmitRequest(
        decision="approved",
        comment="Looks good",
        payload={"test": "data"}
    )
    assert request.decision == "approved"
    assert request.comment == "Looks good"
    print("✓ ReviewSubmitRequest validation works")
    
    # Test ReviewDecisionResponse
    response = ReviewDecisionResponse(
        id=uuid4(),
        project_id=uuid4(),
        episode_id=uuid4(),
        stage_task_id=uuid4(),
        reviewer_user_id=uuid4(),
        decision="approved",
        comment_text="Great work",
        payload_jsonb={"key": "value"},
        created_at="2026-04-11T10:00:00Z"
    )
    assert response.decision == "approved"
    print("✓ ReviewDecisionResponse validation works")
    
    # Test ReviewHistoryItem
    item = ReviewHistoryItem(
        id=uuid4(),
        stage_task_id=uuid4(),
        stage_type="brief",
        reviewer_user_id=uuid4(),
        decision="rejected",
        comment_text="Needs work",
        created_at="2026-04-11T10:00:00Z"
    )
    assert item.stage_type == "brief"
    print("✓ ReviewHistoryItem validation works")
    
    # Test ReviewHistoryResponse
    history = ReviewHistoryResponse(
        episode_id=uuid4(),
        reviews=[item],
        total_count=1
    )
    assert history.total_count == 1
    assert len(history.reviews) == 1
    print("✓ ReviewHistoryResponse validation works")
    
except Exception as e:
    print(f"✗ Schema validation failed: {e}")
    sys.exit(1)

# Test route imports
try:
    from app.api.routes.review import router
    print("✓ Review router imported successfully")
    
    # Check router has the expected routes
    routes = [route.path for route in router.routes]
    expected_routes = [
        "/api/stage-tasks/{stage_task_id}/review",
        "/api/episodes/{episode_id}/reviews"
    ]
    
    for expected in expected_routes:
        if expected in routes:
            print(f"✓ Route {expected} registered")
        else:
            print(f"✗ Route {expected} not found")
            sys.exit(1)
            
except ImportError as e:
    print(f"✗ Failed to import review router: {e}")
    sys.exit(1)

print("\n✅ All Review API components validated successfully!")
print("\nImplemented endpoints:")
print("  POST /api/stage-tasks/{stage_task_id}/review")
print("  GET  /api/episodes/{episode_id}/reviews")
