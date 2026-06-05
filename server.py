import sys
import os
sys.path.append(".")

from flask import Flask, request, jsonify
from flask_cors import CORS

# Security: Import rate limiting module to mitigate Denial of Service (DoS) attacks
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import joblib
import numpy as np
from urllib.parse import urlparse

# ===============================
# IMPORT FEATURE EXTRACTION
# ===============================
from src.features import extract_features

# ===============================
# FLASK APP SETUP
# ===============================
app = Flask(__name__)

# Security: Restrict CORS to localhost origins only
CORS(app, resources={
    r"/predict": {
        "origins": ["http://127.0.0.1", "http://localhost"]
    }
})

# Security: Add HTTP security headers
@app.after_request
def apply_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'; "
    "form-action 'self';"
)
    response.headers["Server"] = "SecureServer"
    return response

# ===============================
# RATE LIMITER (DoS PROTECTION)
# ===============================
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["30 per minute"]
)

# ===============================
# LOAD TRAINED MODEL
# ===============================
MODEL_PATH = "models/phishing_model.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(" Model not found. Train model first.")

model = joblib.load(MODEL_PATH)
EXPECTED_FEATURES = 25

print(" ML model loaded successfully")

# ===============================
# FEATURE NAMES
# ===============================
FEATURE_NAMES = [
    "URL Length",
    "Dot Count",
    "Hyphen Count",
    "Underscore Count",
    "Slash Count",
    "Has @ Symbol",
    "Uses HTTPS",
    "Uses HTTP",
    "IP Address Used",
    "Shortened URL",
    "Digit Count",
    "Letter Count",
    "Digit Ratio",
    "Special Character Ratio",
    "Domain Length",
    "Subdomain Count",
    "TLD Length",
    "Country TLD",
    "Phishing Keywords",
    "Suspicious TLD",
    "Legitimate TLD",
    "Path Length",
    "Query Length",
    "Parameter Count",
    "Structured Domain"
]

# ===============================
# HOME ROUTE (FOR OWASP ZAP TESTING)
# ===============================
@app.route("/")
def home():
    return "SafeScan API Running"

# ===============================
# PREDICTION ENDPOINT
# ===============================
@app.route("/predict", methods=["POST"])
@limiter.limit("10 per minute")
def predict():
    data = request.get_json()
    url = data.get("url") if data else None

    if not url:
        return jsonify({"error": "URL missing"}), 400

    parsed = urlparse(url)

    if not parsed.scheme or not parsed.netloc:
        return jsonify({"error": "Invalid URL format"}), 400

    try:
        features = extract_features(url)

        if len(features) != EXPECTED_FEATURES:
            return jsonify({
                "error": "Feature mismatch",
                "expected": EXPECTED_FEATURES,
                "received": len(features)
            }), 500

        features = features.reshape(1, -1)

        pred = model.predict(features)[0]
        proba = model.predict_proba(features)[0]

        phishing_prob = float(proba[1])
        safe_prob = float(proba[0])

        confidence = phishing_prob if pred == 1 else safe_prob

        feature_values = features.flatten()
        importances = model.feature_importances_

        contributions = importances * feature_values
        top_indices = np.argsort(contributions)[-3:][::-1]

        explanations = []

        for idx in top_indices:
            if contributions[idx] > 0:
                explanations.append(FEATURE_NAMES[idx])

        return jsonify({
            "url": url,
            "prediction": "phishing" if pred == 1 else "legitimate",
            "confidence": round(confidence, 3),
            "explanations": explanations,
            "model": "XGBoost (25 features)"
        })

    except Exception as e:
        return jsonify({
            "error": "Prediction failed",
            "details": str(e)
        }), 500


# ===============================
# RUN SERVER
# ===============================
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)