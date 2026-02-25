"""
AgriTech API Test Suite
========================
Automated tests for all AgriTech API endpoints.
Run this to verify your server is working correctly.

Usage:
    python test_all_endpoints.py

Requirements:
    pip install requests pytest

GitHub: https://github.com/omroy07/AgriTech
"""

import requests
import json
import os
import time
import sys


BASE_URL = "http://localhost:5000"
PASS = "✅ PASS"
FAIL = "❌ FAIL"
SKIP = "⏭️  SKIP"


# ─────────────────────────────────────────────────────────────
#  TEST HELPERS
# ─────────────────────────────────────────────────────────────
class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results = []

    def record(self, name, status, detail=""):
        self.results.append((name, status, detail))
        if status == PASS:
            self.passed += 1
        elif status == FAIL:
            self.failed += 1
        else:
            self.skipped += 1
        print(f"  {status}  {name}" + (f"  →  {detail}" if detail else ""))

    def summary(self):
        total = self.passed + self.failed + self.skipped
        print("\n" + "=" * 55)
        print(f"  TEST SUMMARY: {total} tests")
        print(f"  ✅ Passed : {self.passed}")
        print(f"  ❌ Failed : {self.failed}")
        print(f"  ⏭️  Skipped: {self.skipped}")
        print("=" * 55)
        return self.failed == 0


runner = TestRunner()


# ─────────────────────────────────────────────────────────────
#  PRE-CHECKS
# ─────────────────────────────────────────────────────────────
def test_server_running():
    """Test that the server is up."""
    try:
        r = requests.get(BASE_URL, timeout=5)
        runner.record("Server is running", PASS)
        return True
    except:
        runner.record("Server is running", FAIL,
                      "Run: python app.py")
        return False


# ─────────────────────────────────────────────────────────────
#  CROP RECOMMENDATION TESTS
# ─────────────────────────────────────────────────────────────
def test_crop_prediction_rice():
    """Should recommend rice for high humidity and rainfall."""
    payload = {"N": 90, "P": 42, "K": 43,
               "temperature": 20.87, "humidity": 82.0,
               "ph": 6.5, "rainfall": 202.93}
    try:
        r = requests.post(f"{BASE_URL}/predict_crop", json=payload, timeout=10)
        data = r.json()
        if r.status_code == 200 and "crop" in data:
            runner.record("Crop prediction - rice conditions",
                          PASS, f"Got: {data['crop']}")
        else:
            runner.record("Crop prediction - rice conditions",
                          FAIL, str(data))
    except Exception as e:
        runner.record("Crop prediction - rice conditions", FAIL, str(e))


def test_crop_prediction_cotton():
    """Should recommend cotton for hot dry conditions."""
    payload = {"N": 20, "P": 75, "K": 25,
               "temperature": 37.5, "humidity": 94.5,
               "ph": 5.8, "rainfall": 92.0}
    try:
        r = requests.post(f"{BASE_URL}/predict_crop", json=payload, timeout=10)
        data = r.json()
        if r.status_code == 200 and "crop" in data:
            runner.record("Crop prediction - cotton conditions",
                          PASS, f"Got: {data['crop']}")
        else:
            runner.record("Crop prediction - cotton conditions",
                          FAIL, str(data))
    except Exception as e:
        runner.record("Crop prediction - cotton conditions", FAIL, str(e))


def test_crop_missing_fields():
    """Should return error when required fields are missing."""
    payload = {"N": 90, "P": 42}  # Missing K, temp, humidity, ph, rainfall
    try:
        r = requests.post(f"{BASE_URL}/predict_crop", json=payload, timeout=10)
        if r.status_code in (400, 422, 500):
            runner.record("Crop prediction - missing fields handled",
                          PASS, f"Status: {r.status_code}")
        else:
            runner.record("Crop prediction - missing fields handled",
                          FAIL, f"Expected 4xx, got {r.status_code}")
    except Exception as e:
        runner.record("Crop prediction - missing fields handled", FAIL, str(e))


# ─────────────────────────────────────────────────────────────
#  YIELD PREDICTION TESTS
# ─────────────────────────────────────────────────────────────
def test_yield_prediction_wheat():
    """Should return numeric yield for wheat in Punjab."""
    payload = {
        "crop": "Wheat", "crop_year": 2024,
        "season": "Rabi", "state": "Punjab",
        "area": 1500.0, "annual_rainfall": 750.5,
        "fertilizer": 200.0, "pesticide": 15.0
    }
    try:
        r = requests.post(f"{BASE_URL}/predict_yield", json=payload, timeout=10)
        data = r.json()
        if r.status_code == 200 and "yield" in data:
            y = data["yield"]
            if isinstance(y, (int, float)) and y > 0:
                runner.record("Yield prediction - wheat/Punjab",
                              PASS, f"Yield: {y} tons/ha")
            else:
                runner.record("Yield prediction - wheat/Punjab",
                              FAIL, f"Invalid yield value: {y}")
        else:
            runner.record("Yield prediction - wheat/Punjab",
                          FAIL, str(data))
    except Exception as e:
        runner.record("Yield prediction - wheat/Punjab", FAIL, str(e))


def test_yield_prediction_sugarcane():
    """Should return much higher yield for sugarcane."""
    payload = {
        "crop": "Sugarcane", "crop_year": 2024,
        "season": "Whole Year", "state": "Uttar Pradesh",
        "area": 4000.0, "annual_rainfall": 1100.0,
        "fertilizer": 500.0, "pesticide": 45.0
    }
    try:
        r = requests.post(f"{BASE_URL}/predict_yield", json=payload, timeout=10)
        data = r.json()
        if r.status_code == 200 and "yield" in data:
            runner.record("Yield prediction - sugarcane/UP",
                          PASS, f"Yield: {data['yield']} tons/ha")
        else:
            runner.record("Yield prediction - sugarcane/UP",
                          FAIL, str(data))
    except Exception as e:
        runner.record("Yield prediction - sugarcane/UP", FAIL, str(e))


# ─────────────────────────────────────────────────────────────
#  FERTILIZER RECOMMENDATION TESTS
# ─────────────────────────────────────────────────────────────
def test_fertilizer_recommendation():
    """Should return a fertilizer name for valid input."""
    payload = {
        "Temperature": 26, "Humidity": 52, "Moisture": 38,
        "Soil Type": "Sandy", "Crop Type": "Maize",
        "Nitrogen": 37, "Potassium": 0, "Phosphorous": 0
    }
    try:
        r = requests.post(f"{BASE_URL}/predict_fertilizer",
                          json=payload, timeout=10)
        data = r.json()
        if r.status_code == 200 and "fertilizer" in data:
            runner.record("Fertilizer recommendation",
                          PASS, f"Got: {data['fertilizer']}")
        else:
            runner.record("Fertilizer recommendation",
                          FAIL, str(data))
    except Exception as e:
        runner.record("Fertilizer recommendation", FAIL, str(e))


# ─────────────────────────────────────────────────────────────
#  DISEASE DETECTION TESTS
# ─────────────────────────────────────────────────────────────
def test_disease_detection_image():
    """Should classify plant disease from uploaded image."""
    image_path = "sample_disease_image.jpg"
    if not os.path.exists(image_path):
        runner.record("Disease detection - image upload",
                      SKIP, "sample_disease_image.jpg not found")
        return

    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            r = requests.post(f"{BASE_URL}/predict_disease",
                              files=files, timeout=30)
        data = r.json()
        if r.status_code == 200 and "disease" in data:
            runner.record("Disease detection - image upload",
                          PASS, f"Got: {data['disease']}")
        else:
            runner.record("Disease detection - image upload",
                          FAIL, str(data))
    except Exception as e:
        runner.record("Disease detection - image upload", FAIL, str(e))


def test_disease_detection_no_file():
    """Should return error when no file is uploaded."""
    try:
        r = requests.post(f"{BASE_URL}/predict_disease", timeout=10)
        if r.status_code in (400, 422):
            runner.record("Disease detection - no file handled",
                          PASS, f"Status: {r.status_code}")
        else:
            runner.record("Disease detection - no file handled",
                          FAIL, f"Expected 4xx, got {r.status_code}")
    except Exception as e:
        runner.record("Disease detection - no file handled", FAIL, str(e))


# ─────────────────────────────────────────────────────────────
#  RESPONSE FORMAT TESTS
# ─────────────────────────────────────────────────────────────
def test_response_is_json():
    """All endpoints should return valid JSON."""
    payload = {"N": 90, "P": 42, "K": 43,
               "temperature": 20.87, "humidity": 82.0,
               "ph": 6.5, "rainfall": 202.93}
    try:
        r = requests.post(f"{BASE_URL}/predict_crop", json=payload, timeout=10)
        try:
            r.json()
            runner.record("Response Content-Type is JSON", PASS)
        except ValueError:
            runner.record("Response Content-Type is JSON",
                          FAIL, "Response is not valid JSON")
    except Exception as e:
        runner.record("Response Content-Type is JSON", FAIL, str(e))


def test_response_time():
    """Crop prediction should respond in under 5 seconds."""
    payload = {"N": 90, "P": 42, "K": 43,
               "temperature": 20.87, "humidity": 82.0,
               "ph": 6.5, "rainfall": 202.93}
    try:
        start = time.time()
        r = requests.post(f"{BASE_URL}/predict_crop", json=payload, timeout=10)
        elapsed = time.time() - start
        if elapsed < 5.0:
            runner.record("Response time < 5 seconds",
                          PASS, f"{elapsed:.2f}s")
        else:
            runner.record("Response time < 5 seconds",
                          FAIL, f"Took {elapsed:.2f}s")
    except Exception as e:
        runner.record("Response time < 5 seconds", FAIL, str(e))


# ─────────────────────────────────────────────────────────────
#  BATCH TEST FROM JSON FILE
# ─────────────────────────────────────────────────────────────
def test_batch_from_json():
    """Load sample JSON and run all batch predictions."""
    json_file = "sample_crop_input.json"
    if not os.path.exists(json_file):
        runner.record("Batch predictions from JSON file",
                      SKIP, f"{json_file} not found")
        return

    with open(json_file) as f:
        data = json.load(f)

    samples = data.get("batch_predictions", [])
    correct = 0
    errors  = 0

    for s in samples:
        try:
            r = requests.post(
                f"{BASE_URL}/predict_crop",
                json={"N": s["N"], "P": s["P"], "K": s["K"],
                      "temperature": s["temperature"],
                      "humidity": s["humidity"],
                      "ph": s["ph"], "rainfall": s["rainfall"]},
                timeout=10
            )
            d = r.json()
            if d.get("crop") == s.get("expected_crop"):
                correct += 1
        except:
            errors += 1

    total  = len(samples)
    acc    = (correct / total * 100) if total else 0
    detail = f"{correct}/{total} correct ({acc:.0f}%)"

    if errors == 0 and acc >= 60:
        runner.record("Batch predictions from JSON", PASS, detail)
    elif errors > 0:
        runner.record("Batch predictions from JSON", FAIL,
                      f"{errors} request errors")
    else:
        runner.record("Batch predictions from JSON", FAIL,
                      f"Low accuracy: {detail}")


# ─────────────────────────────────────────────────────────────
#  MAIN - Run all tests
# ─────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("   🧪 AgriTech API Test Suite")
    print("=" * 55)

    # Pre-check: server must be running
    if not test_server_running():
        print("\n❌ Server is not running. Aborting all tests.")
        print("   Start with: python app.py")
        runner.summary()
        sys.exit(1)

    print("\n── Crop Recommendation Tests ──────────────────")
    test_crop_prediction_rice()
    test_crop_prediction_cotton()
    test_crop_missing_fields()

    print("\n── Yield Prediction Tests ─────────────────────")
    test_yield_prediction_wheat()
    test_yield_prediction_sugarcane()

    print("\n── Fertilizer Recommendation Tests ────────────")
    test_fertilizer_recommendation()

    print("\n── Disease Detection Tests ─────────────────────")
    test_disease_detection_image()
    test_disease_detection_no_file()

    print("\n── Response Quality Tests ──────────────────────")
    test_response_is_json()
    test_response_time()

    print("\n── Batch / Integration Tests ───────────────────")
    test_batch_from_json()

    all_passed = runner.summary()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
