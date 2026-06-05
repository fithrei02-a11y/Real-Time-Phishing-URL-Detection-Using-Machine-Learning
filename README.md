# SafeScan: Real-Time Phishing URL Detection Using Machine Learning

## Project Overview

SafeScan is a Final Year Project (FYP) developed to detect phishing URLs in real time using Machine Learning techniques. The system integrates an XGBoost classification model with a Google Chrome Extension and Flask backend API to provide instant phishing detection and user warnings during web browsing.

## Objectives

* Identify important URL-based features associated with phishing websites.
* Develop a machine learning model for phishing URL classification.
* Integrate the trained model into a Google Chrome Extension.
* Evaluate the effectiveness of real-time phishing URL detection.

## Key Features

* Real-time phishing URL detection
* XGBoost machine learning classifier
* Flask API backend
* Google Chrome Extension integration
* URL feature extraction
* Confidence score prediction
* User phishing warning alerts
* OWASP ZAP security assessment
* DoS mitigation implementation

## Technologies Used

* Python
* Flask
* XGBoost
* JavaScript
* HTML/CSS
* Google Chrome Extension API
* OWASP ZAP

## Project Structure

```text
chrome_extension/   # Browser extension source code
models/             # Trained machine learning model
src/                # Feature extraction and training scripts
server.py           # Flask backend server
dos_test.py         # DoS testing script
```

## Machine Learning Model

The system uses the XGBoost algorithm trained on phishing URL datasets to classify URLs as either legitimate or phishing based on extracted URL features.

## Security Validation

The project includes:

* OWASP ZAP vulnerability assessment
* Rate limiting implementation
* DoS attack mitigation testing

## Author

Muhammad Fitri Bin Mohd Aris

Bachelor of Information Technology (Hons) in Computer System Security (BCSS)

Universiti Kuala Lumpur Malaysian Institute of Information Technology (UniKL MIIT)

Academic Year 2026

## Disclaimer

This repository is intended for academic and educational purposes as part of a Final Year Project 2026

