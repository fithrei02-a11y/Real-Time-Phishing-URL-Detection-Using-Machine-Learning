# predict.py - SIMPLE INTERACTIVE VERSION
import joblib
import os
from features import extract_features

MODEL_PATH = "models/phishing_model.pkl"

if not os.path.exists(MODEL_PATH):
    print(f" Model not found at {MODEL_PATH}")
    print("Run train_model.py first")
    exit()

model = joblib.load(MODEL_PATH)

print("="*60)
print("🔍 PHISHING URL DETECTOR")
print("="*60)

while True:
    url = input("\n🌐 Enter URL: ").strip()
    
    if url.lower() in ["exit", "quit", "q"]:
        print("\n👋 Goodbye!")
        break
    
    if not url:
        continue
    
    try:
        features = extract_features(url)
        probability = model.predict_proba([features])[0][1]
        
        if probability > 0.8:
            print(f" PHISHING DETECTED!")
            print(f" Confidence: {probability:.2f}")
        else:
            print(f" SAFE URL")
            print(f" Confidence: {1 - probability:.2f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("-" * 60)