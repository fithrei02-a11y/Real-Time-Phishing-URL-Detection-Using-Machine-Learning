# prepare_dataset.py - FIXED FOR "good" and "bad" labels
import pandas as pd
import os

print("="*60)
print("🛠️ PREPARING DATASET FOR BINARY CLASSIFICATION")
print("Labels: good=SAFE(0), bad=PHISHING(1)")
print("="*60)

# Dataset path
input_file = "data/raw/phishing_site_urls.csv"
output_file = "data/processed/dataset.csv"

# Check dataset
if not os.path.exists(input_file):
    print(f"❌ Dataset not found: {input_file}")
    exit()

# Load dataset
print("\n📥 Loading dataset...")
df = pd.read_csv(input_file)
print(f"✅ Loaded {len(df):,} rows")
print(f"📊 Columns: {df.columns.tolist()}")

# Identify URL column
url_col = None
for col in df.columns:
    if "url" in col.lower():
        url_col = col
        break

if not url_col:
    print("❌ URL column not found!")
    exit()

df.rename(columns={url_col: "url"}, inplace=True)

# Identify label column
label_col = None
for col in df.columns:
    if col.lower() in ["label", "class", "type", "target"]:
        label_col = col
        break

if not label_col:
    print("❌ Label column not found!")
    exit()

df.rename(columns={label_col: "label"}, inplace=True)

# Show original label distribution
print("\n📊 Original label distribution:")
print(df["label"].value_counts())

# Convert labels to numeric (0 & 1) - FIXED
def normalize_label(x):
    x = str(x).lower().strip()
    # GOOD = SAFE (0), BAD = PHISHING (1)
    if x in ["bad", "1", "phishing", "malicious"]:
        return 1  # PHISHING
    else:  # "good", "safe", "benign", etc
        return 0  # SAFE

df["label"] = df["label"].apply(normalize_label)

print("\n✅ Normalized labels:")
print(df["label"].value_counts())

# Clean URLs
def clean_url(url):
    url = str(url).strip().strip('"\'')
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url

df["url"] = df["url"].apply(clean_url)

# Remove duplicates
before = len(df)
df.drop_duplicates(subset=["url"], inplace=True)
after = len(df)
print(f"\n🧹 Removed {before - after} duplicate URLs")

# Save processed dataset
os.makedirs("data/processed", exist_ok=True)
df[["url", "label"]].to_csv(output_file, index=False)

print(f"\n💾 Clean dataset saved: {output_file}")
print(f"Final dataset size: {len(df):,}")

safe_count = (df['label'] == 0).sum()
phishing_count = (df['label'] == 1).sum()
print(f"  • Safe URLs (good): {safe_count:,} ({safe_count/len(df)*100:.1f}%)")
print(f"  • Phishing URLs (bad): {phishing_count:,} ({phishing_count/len(df)*100:.1f}%)")

print("\n" + "="*60)
print("✅ DATASET READY FOR TRAINING")
print("Next: python src/train_model.py")
print("="*60)