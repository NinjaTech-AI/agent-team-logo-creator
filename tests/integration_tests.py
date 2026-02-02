"""
Integration Test Suite for AI Logo Creator Production App

This test suite runs against the deployed production application
to verify all endpoints work correctly in the real environment.

Usage:
    # Run all tests
    python tests/integration_tests.py

    # Run specific test class
    python tests/integration_tests.py TestHealthEndpoint

    # Run with custom URL
    BASE_URL=https://custom-url.com python tests/integration_tests.py

    # Run with pytest for more options
    pytest tests/integration_tests.py -v

Requirements:
    pip install requests pytest
"""

import os
import sys
import time
import requests
import pytest
from dataclasses import dataclass
from typing import Optional


# Configuration
BASE_URL = os.getenv("BASE_URL", "https://agent-team-logo-creator-production.up.railway.app")


@dataclass
class TestResult:
    """Test result container"""
    name: str
    passed: bool
    message: str
    duration: float


class IntegrationTestRunner:
    """Runs integration tests and reports results"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results: list[TestResult] = []

    def run_test(self, name: str, test_func):
        """Run a single test and record result"""
        start = time.time()
        try:
            test_func()
            duration = time.time() - start
            result = TestResult(name, True, "PASSED", duration)
            print(f"  ✅ {name} ({duration:.2f}s)")
        except AssertionError as e:
            duration = time.time() - start
            result = TestResult(name, False, f"FAILED: {str(e)}", duration)
            print(f"  ❌ {name}: {str(e)}")
        except Exception as e:
            duration = time.time() - start
            result = TestResult(name, False, f"ERROR: {str(e)}", duration)
            print(f"  ❌ {name}: {str(e)}")

        self.results.append(result)
        return result.passed

    def summary(self):
        """Print test summary"""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        total_time = sum(r.duration for r in self.results)

        print("\n" + "="*60)
        print(f"Test Results: {passed}/{total} passed ({total_time:.2f}s)")
        print("="*60)

        if passed < total:
            print("\nFailed tests:")
            for r in self.results:
                if not r.passed:
                    print(f"  - {r.name}: {r.message}")

        return passed == total


# =============================================================================
# Health Check Tests
# =============================================================================

class TestHealthEndpoint:
    """Tests for /api/health endpoint"""

    def test_health_returns_200(self):
        """GET /api/health returns 200 status code"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_health_returns_healthy_status(self):
        """GET /api/health returns {\"status\": \"healthy\"}"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        data = response.json()
        assert data == {"status": "healthy"}, f"Expected healthy status, got {data}"


# =============================================================================
# Logo Generation Tests
# =============================================================================

class TestLogoGenerationEndpoint:
    """Tests for /api/generate endpoint"""

    def test_generate_with_business_name_only(self):
        """POST /api/generate with just business name returns success response structure"""
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json={"business_name": "Integration Test Co"},
            timeout=120  # Logo generation can take time
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        # Response should have success field
        assert "success" in data, "Response missing 'success' field"
        # Response should have generation_id or error
        assert "generation_id" in data or "error" in data, "Response missing 'generation_id' or 'error'"

        # If successful, should have logo URLs
        if data["success"]:
            assert data.get("logo_url") or data.get("logo_urls"), "Success response missing logo URLs"

    def test_generate_with_all_parameters(self):
        """POST /api/generate with all parameters returns success response structure"""
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json={
                "business_name": "Full Test Inc",
                "style": "modern",
                "description": "A technology company focused on innovation",
                "size": "1024x1024",
                "resolution": "high",
                "filters": ["vibrant", "gradient"],
                "transparency": False,
                "preview_mode": False
            },
            timeout=180  # Full generation with multiple images
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "success" in data, "Response missing 'success' field"

        if data["success"]:
            assert data.get("logo_urls"), "Success should return logo_urls array"

    def test_generate_preview_mode(self):
        """POST /api/generate with preview_mode=true returns quickly"""
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json={
                "business_name": "Preview Test",
                "style": "minimalist",
                "preview_mode": True
            },
            timeout=60  # Preview should be faster
        )
        duration = time.time() - start

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "success" in data, "Response missing 'success' field"

        # Preview mode should generate only 1 logo (vs 4 for full mode)
        if data["success"] and data.get("logo_urls"):
            assert len(data["logo_urls"]) == 1, f"Preview mode should return 1 logo, got {len(data['logo_urls'])}"

    def test_generate_all_styles(self):
        """POST /api/generate accepts all documented styles"""
        styles = ["minimalist", "modern", "classic", "playful", "professional", "vintage"]

        for style in styles:
            response = requests.post(
                f"{BASE_URL}/api/generate",
                json={
                    "business_name": f"{style.capitalize()} Test",
                    "style": style,
                    "preview_mode": True  # Use preview for speed
                },
                timeout=60
            )
            assert response.status_code == 200, f"Style '{style}' failed with status {response.status_code}"

            data = response.json()
            # Should get a valid response (success or documented error)
            assert "success" in data, f"Style '{style}' response missing 'success' field"


# =============================================================================
# Prompt Improvement Tests
# =============================================================================

class TestPromptImprovementEndpoint:
    """Tests for /api/improve-prompt endpoint"""

    def test_improve_prompt_basic(self):
        """POST /api/improve-prompt returns improved prompt and preview"""
        response = requests.post(
            f"{BASE_URL}/api/improve-prompt",
            json={
                "business_name": "Improve Test LLC",
                "style": "modern"
            },
            timeout=90
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "success" in data, "Response missing 'success' field"

        if data["success"]:
            assert data.get("improved_prompt"), "Success response missing 'improved_prompt'"
            assert data.get("preview_url"), "Success response missing 'preview_url'"

    def test_improve_prompt_with_description(self):
        """POST /api/improve-prompt includes description in improvement"""
        response = requests.post(
            f"{BASE_URL}/api/improve-prompt",
            json={
                "business_name": "Describe Test Co",
                "style": "professional",
                "description": "We build software for healthcare"
            },
            timeout=90
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "success" in data, "Response missing 'success' field"


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling"""

    def test_generate_missing_business_name(self):
        """POST /api/generate without business_name returns validation error"""
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json={"style": "modern"},
            timeout=30
        )
        # FastAPI should return 422 for missing required field
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

        # Verify the error message mentions business_name
        data = response.json()
        assert "detail" in data, "Validation error should have 'detail' field"

    def test_generate_invalid_json(self):
        """POST /api/generate with invalid JSON returns error"""
        response = requests.post(
            f"{BASE_URL}/api/generate",
            data="not valid json",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 422, f"Expected 422 for invalid JSON, got {response.status_code}"

    def test_nonexistent_endpoint(self):
        """GET /api/nonexistent returns 404 or handled gracefully"""
        response = requests.get(
            f"{BASE_URL}/api/nonexistent",
            timeout=30
        )
        # Should be 404 or redirected to SPA
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"


# =============================================================================
# Frontend Serving Tests
# =============================================================================

class TestFrontendServing:
    """Tests for static frontend serving"""

    def test_root_serves_html(self):
        """GET / returns HTML page"""
        response = requests.get(f"{BASE_URL}/", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/html" in response.headers.get("Content-Type", ""), "Root should serve HTML"

    def test_root_contains_app_element(self):
        """GET / contains React root element"""
        response = requests.get(f"{BASE_URL}/", timeout=30)
        assert 'id="root"' in response.text, "HTML should contain root element for React"

    def test_assets_accessible(self):
        """Static assets are accessible"""
        # First get the HTML to find asset paths
        response = requests.get(f"{BASE_URL}/", timeout=30)

        # Check if there are JS assets referenced
        if '/assets/' in response.text:
            # Try to access at least one asset
            import re
            assets = re.findall(r'/assets/[^"\']+', response.text)
            if assets:
                asset_url = f"{BASE_URL}{assets[0]}"
                asset_response = requests.get(asset_url, timeout=30)
                assert asset_response.status_code == 200, f"Asset {assets[0]} not accessible"


# =============================================================================
# Response Structure Tests
# =============================================================================

class TestResponseStructure:
    """Tests for API response structure compliance"""

    def test_generate_response_structure(self):
        """POST /api/generate returns correctly structured response"""
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json={"business_name": "Structure Test"},
            timeout=120
        )
        data = response.json()

        # Required fields
        assert "success" in data, "Missing 'success' field"

        if data["success"]:
            # Success response fields
            assert "generation_id" in data, "Success response missing 'generation_id'"
            assert "logo_url" in data or "logo_urls" in data, "Success response missing logo URLs"
        else:
            # Error response fields
            assert "error" in data, "Error response missing 'error' field"

    def test_improve_prompt_response_structure(self):
        """POST /api/improve-prompt returns correctly structured response"""
        response = requests.post(
            f"{BASE_URL}/api/improve-prompt",
            json={"business_name": "Structure Test", "style": "modern"},
            timeout=90
        )
        data = response.json()

        # Required fields
        assert "success" in data, "Missing 'success' field"

        if data["success"]:
            assert "improved_prompt" in data, "Success response missing 'improved_prompt'"
            assert "preview_url" in data, "Success response missing 'preview_url'"
        else:
            assert "error" in data, "Error response missing 'error' field"


# =============================================================================
# Main Test Runner
# =============================================================================

def run_all_tests():
    """Run all integration tests"""
    print(f"\n{'='*60}")
    print("AI Logo Creator - Integration Test Suite")
    print(f"{'='*60}")
    print(f"Target: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    runner = IntegrationTestRunner(BASE_URL)

    # Health Check Tests
    print("📋 Health Check Tests")
    health_tests = TestHealthEndpoint()
    runner.run_test("health_returns_200", health_tests.test_health_returns_200)
    runner.run_test("health_returns_healthy_status", health_tests.test_health_returns_healthy_status)

    # Error Handling Tests (run early as they're quick)
    print("\n📋 Error Handling Tests")
    error_tests = TestErrorHandling()
    runner.run_test("generate_missing_business_name", error_tests.test_generate_missing_business_name)
    runner.run_test("generate_invalid_json", error_tests.test_generate_invalid_json)
    runner.run_test("nonexistent_endpoint", error_tests.test_nonexistent_endpoint)

    # Frontend Tests
    print("\n📋 Frontend Serving Tests")
    frontend_tests = TestFrontendServing()
    runner.run_test("root_serves_html", frontend_tests.test_root_serves_html)
    runner.run_test("root_contains_app_element", frontend_tests.test_root_contains_app_element)
    runner.run_test("assets_accessible", frontend_tests.test_assets_accessible)

    # Response Structure Tests (with API calls)
    print("\n📋 Response Structure Tests")
    structure_tests = TestResponseStructure()
    runner.run_test("generate_response_structure", structure_tests.test_generate_response_structure)
    runner.run_test("improve_prompt_response_structure", structure_tests.test_improve_prompt_response_structure)

    # Logo Generation Tests (these involve actual API calls, may depend on OPENAI_API_KEY)
    print("\n📋 Logo Generation Tests (may require OPENAI_API_KEY)")
    logo_tests = TestLogoGenerationEndpoint()
    runner.run_test("generate_with_business_name_only", logo_tests.test_generate_with_business_name_only)
    runner.run_test("generate_preview_mode", logo_tests.test_generate_preview_mode)

    # Prompt Improvement Tests
    print("\n📋 Prompt Improvement Tests (may require OPENAI_API_KEY)")
    prompt_tests = TestPromptImprovementEndpoint()
    runner.run_test("improve_prompt_basic", prompt_tests.test_improve_prompt_basic)
    runner.run_test("improve_prompt_with_description", prompt_tests.test_improve_prompt_with_description)

    # Summary
    all_passed = runner.summary()

    return all_passed


def run_quick_tests():
    """Run only quick tests that don't require OpenAI API"""
    print(f"\n{'='*60}")
    print("AI Logo Creator - Quick Integration Tests")
    print(f"{'='*60}")
    print(f"Target: {BASE_URL}")
    print("(Skipping tests that require OPENAI_API_KEY)")
    print(f"{'='*60}\n")

    runner = IntegrationTestRunner(BASE_URL)

    # Health Check Tests
    print("📋 Health Check Tests")
    health_tests = TestHealthEndpoint()
    runner.run_test("health_returns_200", health_tests.test_health_returns_200)
    runner.run_test("health_returns_healthy_status", health_tests.test_health_returns_healthy_status)

    # Error Handling Tests
    print("\n📋 Error Handling Tests")
    error_tests = TestErrorHandling()
    runner.run_test("generate_missing_business_name", error_tests.test_generate_missing_business_name)
    runner.run_test("generate_invalid_json", error_tests.test_generate_invalid_json)
    runner.run_test("nonexistent_endpoint", error_tests.test_nonexistent_endpoint)

    # Frontend Tests
    print("\n📋 Frontend Serving Tests")
    frontend_tests = TestFrontendServing()
    runner.run_test("root_serves_html", frontend_tests.test_root_serves_html)
    runner.run_test("root_contains_app_element", frontend_tests.test_root_contains_app_element)
    runner.run_test("assets_accessible", frontend_tests.test_assets_accessible)

    # Summary
    all_passed = runner.summary()

    return all_passed


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            success = run_quick_tests()
        elif sys.argv[1] == "--help":
            print(__doc__)
            sys.exit(0)
        else:
            # Run with pytest for specific test selection
            pytest.main([__file__, "-v"] + sys.argv[1:])
            sys.exit(0)
    else:
        success = run_all_tests()

    sys.exit(0 if success else 1)
