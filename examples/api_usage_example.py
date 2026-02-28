"""
AgriTech API Usage Example
==========================
This script demonstrates how to use all the AgriTech API endpoints
from a Python script (without opening a browser).

Requirements:
    pip install requests pillow

Usage:
    1. Start the AgriTech server: python app.py
    2. Run this script:           python api_usage_example.py

GitHub: https://github.com/omroy07/AgriTech
"""

import requests
import json
import os
import sys
from pathlib import Path


# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
BASE_URL    = "http://localhost:5000"
TIMEOUT     = 30          # seconds
VERBOSE     = True        # set False to suppress extra output

HEADERS = {"Content-Type": "application/json"}


# ─────────────────────────────────────────────
#  HELPER UTILITIES
# ─────────────────────────────────────────────
def _log(msg):
    if VERBOSE:
        print(msg)


def _handle_response(response):
    """Parse JSON response and return (data, error)."""
    try:
        data = response.json()
        if response.status_code == 200:
            return data, None
        else:
            return None, data.get("error", f"HTTP {response.status_code}")
    except Exception as e:
        return None, str(e)


def check_server():
    """Check if the AgriTech server is running."""
    try:
        r = requests.get(BASE_URL, timeout=5)
        _log(f"✅ Server is running at {BASE_URL}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Server not running at {BASE_URL}")
        print("   Start it with: python app.py")
        return False


# ─────────────────────────────────────────────
#  1. CROP RECOMMENDATION
# ─────────────────────────────────────────────
def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    """
    Get crop recommendation based on soil and climate parameters.

    Parameters:
        N           (float): Nitrogen content in soil (kg/ha)
        P           (float): Phosphorous content in soil (kg/ha)
        K           (float): Potassium content in soil (kg/ha)
        temperature (float): Temperature in Celsius
        humidity    (float): Relative humidity (%)
        ph          (float): Soil pH value (0-14)
        rainfall    (float): Annual rainfall in mm

    Returns:
        dict: {'crop': str, 'confidence': float} or {'error': str}

    Example:
        >>> result = predict_crop(90, 42, 43, 20.87, 82.0, 6.5, 202.93)
        >>> print(result['crop'])  # 'rice'
    """
    endpoint = f"{BASE_URL}/predict_crop"
    payload  = {
        "N": N, "P": P, "K": K,
        "temperature": temperature,
        "humidity":    humidity,
        "ph":          ph,
        "rainfall":    rainfall
    }

    _log(f"\n🌾 Calling Crop Recommendation API...")
    _log(f"   Payload: {payload}")

    try:
        response = requests.post(endpoint, json=payload,
                                 headers=HEADERS, timeout=TIMEOUT)
        data, err = _handle_response(response)
        if err:
            return {"error": err}
        _log(f"   ✅ Response: {data}")
        return data
    except requests.exceptions.ConnectionError:
        return {"error": "Server not running"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
#  2. YIELD PREDICTION
# ─────────────────────────────────────────────
def predict_yield(crop, crop_year, season, state,
                  area, annual_rainfall, fertilizer, pesticide):
    """
    Predict crop yield (tons per hectare).

    Parameters:
        crop            (str):   Crop name (e.g. 'Wheat', 'Rice')
        crop_year       (int):   Year of cultivation
        season          (str):   'Kharif' | 'Rabi' | 'Zaid' | 'Whole Year'
        state           (str):   Indian state name
        area            (float): Area under cultivation in hectares
        annual_rainfall (float): Annual rainfall in mm
        fertilizer      (float): Fertilizer used in kg/ha
        pesticide       (float): Pesticide used in kg/ha

    Returns:
        dict: {'yield': float, 'unit': 'tons/ha'} or {'error': str}

    Example:
        >>> result = predict_yield('Wheat', 2024, 'Rabi', 'Punjab',
        ...                        1500, 750.5, 200, 15)
        >>> print(result['yield'])  # e.g. 4.2
    """
    endpoint = f"{BASE_URL}/predict_yield"
    payload  = {
        "crop":            crop,
        "crop_year":       crop_year,
        "season":          season,
        "state":           state,
        "area":            area,
        "annual_rainfall": annual_rainfall,
        "fertilizer":      fertilizer,
        "pesticide":       pesticide
    }

    _log(f"\n📈 Calling Yield Prediction API...")
    _log(f"   Crop: {crop}, Year: {crop_year}, Season: {season}, State: {state}")

    try:
        response = requests.post(endpoint, json=payload,
                                 headers=HEADERS, timeout=TIMEOUT)
        data, err = _handle_response(response)
        if err:
            return {"error": err}
        _log(f"   ✅ Predicted yield: {data.get('yield')} tons/ha")
        return data
    except requests.exceptions.ConnectionError:
        return {"error": "Server not running"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
#  3. DISEASE DETECTION (Image Upload)
# ─────────────────────────────────────────────
def detect_disease(image_path):
    """
    Detect plant disease from a leaf image.

    Parameters:
        image_path (str): Path to the plant leaf image (JPG/PNG)

    Returns:
        dict: {
            'disease': str,
            'confidence': float,
            'is_healthy': bool,
            'treatment': str
        } or {'error': str}

    Example:
        >>> result = detect_disease('leaf.jpg')
        >>> print(result['disease'])  # 'Tomato___Early_blight'
        >>> print(result['treatment'])
    """
    endpoint = f"{BASE_URL}/predict_disease"

    if not os.path.exists(image_path):
        return {"error": f"Image file not found: {image_path}"}

    _log(f"\n🌿 Calling Disease Detection API...")
    _log(f"   Image: {image_path}")

    try:
        with open(image_path, "rb") as img_file:
            files    = {"file": (Path(image_path).name, img_file, "image/jpeg")}
            response = requests.post(endpoint, files=files, timeout=TIMEOUT)
        data, err = _handle_response(response)
        if err:
            return {"error": err}
        _log(f"   ✅ Detected: {data.get('disease')} ({data.get('confidence')}%)")
        return data
    except requests.exceptions.ConnectionError:
        return {"error": "Server not running"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
#  4. FERTILIZER RECOMMENDATION
# ─────────────────────────────────────────────
def recommend_fertilizer(temperature, humidity, moisture, soil_type,
                          crop_type, nitrogen, potassium, phosphorous):
    """
    Get fertilizer recommendation based on soil and crop data.

    Parameters:
        temperature  (float): Soil temperature in Celsius
        humidity     (float): Humidity (%)
        moisture     (float): Soil moisture (%)
        soil_type    (str):   'Sandy' | 'Loamy' | 'Black' | 'Red' | 'Clayey'
        crop_type    (str):   'Maize' | 'Sugarcane' | 'Cotton' | etc.
        nitrogen     (int):   Current N level in soil
        potassium    (int):   Current K level in soil
        phosphorous  (int):   Current P level in soil

    Returns:
        dict: {'fertilizer': str, 'recommendation': str} or {'error': str}

    Example:
        >>> result = recommend_fertilizer(26, 52, 38, 'Sandy', 'Maize', 37, 0, 0)
        >>> print(result['fertilizer'])  # e.g. 'Urea'
    """
    endpoint = f"{BASE_URL}/predict_fertilizer"
    payload  = {
        "Temperature":  temperature,
        "Humidity":     humidity,
        "Moisture":     moisture,
        "Soil Type":    soil_type,
        "Crop Type":    crop_type,
        "Nitrogen":     nitrogen,
        "Potassium":    potassium,
        "Phosphorous":  phosphorous
    }

    _log(f"\n🧪 Calling Fertilizer Recommendation API...")
    _log(f"   Crop: {crop_type}, Soil: {soil_type}")

    try:
        response = requests.post(endpoint, json=payload,
                                 headers=HEADERS, timeout=TIMEOUT)
        data, err = _handle_response(response)
        if err:
            return {"error": err}
        _log(f"   ✅ Recommended: {data.get('fertilizer')}")
        return data
    except requests.exceptions.ConnectionError:
        return {"error": "Server not running"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
#  5. SOIL CLASSIFICATION
# ─────────────────────────────────────────────
def classify_soil(image_path):
    """
    Classify soil type from an image.

    Parameters:
        image_path (str): Path to the soil image file

    Returns:
        dict: {'soil_type': str, 'confidence': float,
               'properties': dict} or {'error': str}

    Example:
        >>> result = classify_soil('soil_sample.jpg')
        >>> print(result['soil_type'])  # e.g. 'Black Cotton Soil'
    """
    endpoint = f"{BASE_URL}/classify_soil"

    if not os.path.exists(image_path):
        return {"error": f"Image not found: {image_path}"}

    _log(f"\n🪨 Calling Soil Classification API...")

    try:
        with open(image_path, "rb") as f:
            files    = {"file": (Path(image_path).name, f, "image/jpeg")}
            response = requests.post(endpoint, files=files, timeout=TIMEOUT)
        data, err = _handle_response(response)
        if err:
            return {"error": err}
        _log(f"   ✅ Soil type: {data.get('soil_type')}")
        return data
    except requests.exceptions.ConnectionError:
        return {"error": "Server not running"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
#  6. BATCH PROCESSING FROM JSON FILE
# ─────────────────────────────────────────────
def batch_crop_prediction(json_file_path):
    """
    Run crop predictions for multiple samples from a JSON file.

    Parameters:
        json_file_path (str): Path to sample_crop_input.json

    Returns:
        list: List of prediction results
    """
    _log(f"\n📦 Running batch predictions from: {json_file_path}")

    if not os.path.exists(json_file_path):
        return {"error": f"JSON file not found: {json_file_path}"}

    with open(json_file_path, "r") as f:
        data = json.load(f)

    results = []
    for sample in data.get("batch_predictions", []):
        result = predict_crop(
            sample["N"], sample["P"], sample["K"],
            sample["temperature"], sample["humidity"],
            sample["ph"], sample["rainfall"]
        )
        results.append({
            "id":       sample["id"],
            "expected": sample.get("expected_crop", "unknown"),
            "result":   result
        })

    return results


# ─────────────────────────────────────────────
#  MAIN: DEMO ALL ENDPOINTS
# ─────────────────────────────────────────────
def main():
    print("=" * 55)
    print("   🌾 AgriTech API - Python Usage Examples")
    print("=" * 55)

    # Check if server is up
    if not check_server():
        print("\n💡 To start the server:")
        print("   cd AgriTech && python app.py")
        sys.exit(1)

    print("\n" + "─" * 55)

    # ── 1. Crop Recommendation ──────────────────────
    print("\n[1/5] CROP RECOMMENDATION")
    crop_result = predict_crop(
        N=90, P=42, K=43,
        temperature=20.87, humidity=82.0,
        ph=6.5, rainfall=202.93
    )
    if "error" not in crop_result:
        print(f"  ✅ Recommended Crop : {crop_result.get('crop', 'N/A')}")
        print(f"     Confidence       : {crop_result.get('confidence', 'N/A')}%")
    else:
        print(f"  ❌ Error: {crop_result['error']}")

    # ── 2. Yield Prediction ─────────────────────────
    print("\n[2/5] YIELD PREDICTION")
    yield_result = predict_yield(
        crop="Wheat", crop_year=2024,
        season="Rabi", state="Punjab",
        area=1500.0, annual_rainfall=750.5,
        fertilizer=200.0, pesticide=15.0
    )
    if "error" not in yield_result:
        yld = yield_result.get('yield', 'N/A')
        print(f"  ✅ Predicted Yield   : {yld} tons/ha")
        print(f"     Total Production  : {float(yld) * 1500:.1f} tons (for 1500 ha)")
    else:
        print(f"  ❌ Error: {yield_result['error']}")

    # ── 3. Disease Detection ────────────────────────
    print("\n[3/5] DISEASE DETECTION")
    if os.path.exists("sample_disease_image.jpg"):
        disease_result = detect_disease("sample_disease_image.jpg")
        if "error" not in disease_result:
            status = "Healthy ✅" if disease_result.get("is_healthy") else "Diseased ⚠️"
            print(f"  ✅ Status     : {status}")
            print(f"     Disease    : {disease_result.get('disease', 'N/A')}")
            print(f"     Confidence : {disease_result.get('confidence', 'N/A')}%")
            print(f"     Treatment  : {disease_result.get('treatment', 'N/A')}")
        else:
            print(f"  ❌ Error: {disease_result['error']}")
    else:
        print("  ⚠️  sample_disease_image.jpg not found in examples folder.")
        print("       Add a plant leaf JPG image to test disease detection.")

    # ── 4. Fertilizer Recommendation ───────────────
    print("\n[4/5] FERTILIZER RECOMMENDATION")
    fert_result = recommend_fertilizer(
        temperature=26, humidity=52, moisture=38,
        soil_type="Sandy", crop_type="Maize",
        nitrogen=37, potassium=0, phosphorous=0
    )
    if "error" not in fert_result:
        print(f"  ✅ Fertilizer    : {fert_result.get('fertilizer', 'N/A')}")
        print(f"     Recommendation: {fert_result.get('recommendation', 'N/A')}")
    else:
        print(f"  ❌ Error: {fert_result['error']}")

    # ── 5. Batch Predictions ────────────────────────
    print("\n[5/5] BATCH CROP PREDICTIONS (from JSON file)")
    batch_results = batch_crop_prediction("sample_crop_input.json")
    if isinstance(batch_results, list):
        print(f"  Processed {len(batch_results)} samples:")
        for r in batch_results:
            predicted = r['result'].get('crop', 'error')
            expected  = r['expected']
            match     = "✅" if predicted == expected else "❌"
            print(f"  {match}  ID {r['id']}: expected={expected}, got={predicted}")
    else:
        print(f"  ❌ Error: {batch_results.get('error')}")

    print("\n" + "=" * 55)
    print("   ✅ Demo Complete!")
    print("=" * 55)


if __name__ == "__main__":
    main()
