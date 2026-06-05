# train_model.py - XGBOOST VERSION WITH 25 FEATURES
import pandas as pd
import numpy as np
import joblib
import os
import sys
import time
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

# ========== FIXED IMPORT SECTION ==========
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from features import extract_features
    print(" Features module imported successfully")
except ImportError as e:
    print(f" Import Error: {e}")
    print(f"Current path: {sys.path}")
    print(f"Looking in: {src_dir}")

    try:
        sys.path.insert(0, current_dir)
        from src.features import extract_features
        print(" Features imported from src.features")
    except ImportError:
        print(" All import attempts failed")
        print("Make sure features.py exists in src/ folder")
        sys.exit(1)

print("=" * 60)
print("PHISHING DETECTION MODEL TRAINING (XGBOOST)")
print("=" * 60)

# 1. Load dataset
print("\nLoading dataset...")
try:
    df = pd.read_csv("data/processed/dataset.csv")
    print(f"Dataset loaded: {len(df):,} samples")
except FileNotFoundError:
    sys.exit("❌ Error: Dataset file not found")

# 2. Dataset statistics
safe_count = (df['label'] == 0).sum()
phishing_count = (df['label'] == 1).sum()
total = len(df)

print(f"\nDataset statistics:")
print(f"• Safe URLs: {safe_count:,} ({safe_count/total*100:.1f}%)")
print(f"• Phishing URLs: {phishing_count:,} ({phishing_count/total*100:.1f}%)")

# 3. Extract features
print(f"\nExtracting features from {len(df):,} URLs...")
X, y = [], []
fail_count = 0
start_time = time.time()

batch_size = 50000

for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i+batch_size]

    for _, row in batch.iterrows():
        try:
            features = extract_features(row['url'])

            if len(features) >= 24:
                X.append(features)
                y.append(row['label'])
            else:
                fail_count += 1
        except:
            fail_count += 1

    processed = min(i + batch_size, len(df))

    if i % 100000 == 0 or processed == len(df):
        print(f"  Processed: {processed:,}/{len(df):,} ({processed/len(df)*100:.1f}%)")

elapsed_time = time.time() - start_time
print(f"Feature extraction completed in {elapsed_time:.1f} seconds")

if len(X) == 0:
    sys.exit(" Error: No valid features extracted")

X = np.array(X)
y = np.array(y)

# 4. Split dataset
print(f"\nPreparing training and testing sets...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"• Training samples: {X_train.shape[0]:,}")
print(f"• Testing samples: {X_test.shape[0]:,}")

# 5. Train XGBoost model
print(f"\nTraining XGBoost classifier...")
train_start = time.time()

model = XGBClassifier(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.05,
    random_state=42,
    n_jobs=-1,
    eval_metric='logloss'
)

model.fit(X_train, y_train)

train_time = time.time() - train_start
print(f"Training completed in {train_time:.1f} seconds")

# 6. Evaluate model
print(f"\nEvaluating model performance...")
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision_safe = precision_score(y_test, y_pred, pos_label=0)
recall_safe = recall_score(y_test, y_pred, pos_label=0)
f1_safe = f1_score(y_test, y_pred, pos_label=0)

precision_phish = precision_score(y_test, y_pred, pos_label=1)
recall_phish = recall_score(y_test, y_pred, pos_label=1)
f1_phish = f1_score(y_test, y_pred, pos_label=1)

precision_all = np.array([precision_safe, precision_phish])
recall_all = np.array([recall_safe, recall_phish])
f1_all = np.array([f1_safe, f1_phish])
support_all = np.array([(y_test == 0).sum(), (y_test == 1).sum()])

macro_precision = precision_all.mean()
macro_recall = recall_all.mean()
macro_f1 = f1_all.mean()

weighted_precision = np.average(precision_all, weights=support_all)
weighted_recall = np.average(recall_all, weights=support_all)
weighted_f1 = np.average(f1_all, weights=support_all)

print(f"\n CLASSIFICATION METRICS")
print("=" * 70)
print(f"{'':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
print("-" * 70)
print(f"{'(0) Safe':<15} {precision_safe:<12.2%} {recall_safe:<12.2%} {f1_safe:<12.2%} {support_all[0]:<10,}")
print(f"{'(1) Phishing':<15} {precision_phish:<12.2%} {recall_phish:<12.2%} {f1_phish:<12.2%} {support_all[1]:<10,}")
print("-" * 70)
print(f"{'macro avg':<15} {macro_precision:<12.2%} {macro_recall:<12.2%} {macro_f1:<12.2%} {support_all.sum():<10,}")
print(f"{'weighted avg':<15} {weighted_precision:<12.2%} {weighted_recall:<12.2%} {weighted_f1:<12.2%} {support_all.sum():<10,}")
print("-" * 70)
print(f"{'accuracy':<15} {accuracy:<12.2%} {'':<12} {'':<12} {len(y_test):<10,}")

# 7. Save model
os.makedirs("models", exist_ok=True)
model_path = "models/phishing_model.pkl"
joblib.dump(model, model_path)

print(f"\n Model saved to: {model_path}")
print(f"Model uses {X.shape[1]} features")

# 8. Feature importance
importances = model.feature_importances_
top_features = np.argsort(importances)[-5:][::-1]

print(f"\n TOP 5 IMPORTANT FEATURES:")

feature_names = [
    "URL Length", "Dot Count", "Hyphen Count", "Underscore Count", "Slash Count",
    "Has @", "HTTPS", "HTTP", "Has IP", "Shortened URL",
    "Digit Count", "Letter Count", "Digit Ratio", "Special Char Ratio",
    "Domain Length", "Subdomain Count", "TLD Length", "Country TLD",
    "Phishing Keywords", "Suspicious TLD", "Legitimate TLD",
    "Path Length", "Query Length", "Parameter Count",
    "Structured Domain"
]

for idx in top_features:
    if idx < len(feature_names):
        print(f"• {feature_names[idx]:<20} (F{idx}): {importances[idx]:.4f}")

print("\n" + "=" * 60)
print(" XGBOOST TRAINING COMPLETED SUCCESSFULLY")
print("=" * 60)