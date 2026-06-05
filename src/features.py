import numpy as np
import re
from urllib.parse import urlparse

def extract_features(url):
    """Extract 25 features from URL for phishing detection"""
    url = str(url).lower().strip()
    features = []
    
    # 1. URL STRUCTURE (6 features)
    features.append(len(url))
    features.append(url.count('.'))
    features.append(url.count('-'))
    features.append(url.count('_'))
    features.append(url.count('/'))
    features.append(1.0 if '@' in url else 0.0)
    
    # 2. SECURITY & PROTOCOL (4 features)
    features.append(1.0 if url.startswith('https') else 0.0)
    features.append(1.0 if url.startswith('http://') else 0.0)
    
    ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    features.append(1.0 if re.search(ip_pattern, url) else 0.0)
    
    shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 'ow.ly', 'is.gd']
    features.append(1.0 if any(s in url for s in shorteners) else 0.0)
    
    # 3. CHARACTER ANALYSIS (4 features)
    features.append(sum(c.isdigit() for c in url))
    features.append(sum(c.isalpha() for c in url))
    
    if len(url) > 0:
        features.append(features[-2] / len(url))
    else:
        features.append(0.0)
    
    special_chars = sum(1 for c in url if not c.isalnum() and c not in ['.', '-', '_', '/', ':', '?', '=', '&'])
    features.append(special_chars / max(1, len(url)))
    
    # 4. DOMAIN ANALYSIS (4 features)
    domain = ""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc if parsed.netloc else parsed.path.split('/')[0]
        
        features.append(len(domain))
        features.append(domain.count('.'))
        
        domain_parts = domain.split('.')
        tld = domain_parts[-1] if domain_parts else ""
        features.append(len(tld))
        
        country_tlds = {'my', 'sg', 'uk', 'us', 'au', 'ca', 'de', 'fr', 'jp', 'cn'}
        is_country_tld = False
        if domain_parts:
            if domain_parts[-1] in country_tlds:
                is_country_tld = True
            elif len(domain_parts) >= 2:
                last_two = f"{domain_parts[-2]}.{domain_parts[-1]}"
                if re.match(r'^(edu|gov|com|org|net)\.(my|sg|uk|au)$', last_two):
                    is_country_tld = True
        
        features.append(1.0 if is_country_tld else 0.0)
        
    except:
        features.extend([0, 0, 0, 0])
        domain = url
    
    # 5. PHISHING PATTERN DETECTION (6 features)
    phishing_keywords = [
        'login', 'secure', 'verify', 'update', 'account', 'banking',
        'password', 'confirm', 'auth', 'signin', 'wallet', 'payment'
    ]
    features.append(sum(1 for kw in phishing_keywords if kw in url))
    
    suspicious_tlds = ['.xyz', '.top', '.tk', '.ml', '.ga', '.cf', '.gq']
    features.append(1.0 if any(tld in url for tld in suspicious_tlds) else 0.0)
    
    legitimate_tlds = ['.com', '.org', '.net', '.edu', '.gov']
    features.append(1.0 if any(tld in url for tld in legitimate_tlds) else 0.0)
    
    # Path analysis
    try:
        if 'parsed' in locals():
            features.append(len(parsed.path))
            features.append(len(parsed.query))
            features.append(parsed.query.count('&'))
        else:
            features.extend([0, 0, 0])
    except:
        features.extend([0, 0, 0])
    
    # 6. STRUCTURED COUNTRY DOMAIN (1 feature)
    is_structured = False
    if domain:
        structured_patterns = [
            r'\.edu\.(my|sg|uk|au)$',
            r'\.gov\.(my|sg|uk|au)$',
            r'\.com\.(my|sg|uk|au)$',
            r'\.org\.(my|sg|uk|au)$',
            r'\.net\.(my|sg|uk)$',
        ]
        
        for pattern in structured_patterns:
            if re.search(pattern, domain):
                is_structured = True
                break
    
    features.append(1.0 if is_structured else 0.0)
    
    # Ensure 25 features total
    while len(features) < 25:
        features.append(0.0)
    
    return np.array(features[:25], dtype=float)