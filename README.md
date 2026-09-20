# BotSentinel Backend

FastAPI backend for **BotSentinel**, a machine-learning-based network security prototype for detecting botnet-related traffic from network flow features.

The backend exposes a REST API that validates network-flow data, applies the preprocessing embedded in the trained machine-learning pipeline, and returns a botnet classification with a probability and confidence score.

> **Academic project:** Machine Learning-Based Botnet Traffic Detection Using the CTU-13 Dataset

---

## Overview

BotSentinel is designed as a lightweight ML-powered traffic detection system.

The backend is responsible for:

* Receiving network-flow features through a REST API
* Validating incoming traffic data
* Normalizing network port representations
* Applying the trained preprocessing pipeline
* Running the trained Random Forest classifier
* Returning botnet/non-botnet predictions
* Providing a botnet probability and confidence score
* Exposing health and service-status endpoints
* Restricting cross-origin requests to the deployed frontend
* Logging prediction events without storing submitted traffic-flow details

The backend is built with **FastAPI** and serves a serialized scikit-learn pipeline using `joblib`.

---

## Architecture

```text
                    ┌─────────────────────────┐
                    │     BotSentinel UI      │
                    │     Next.js / Vercel    │
                    └────────────┬────────────┘
                                 │
                                 │ HTTPS / JSON
                                 ▼
                    ┌─────────────────────────┐
                    │     FastAPI Backend      │
                    │                         │
                    │  Request Validation     │
                    │          │              │
                    │          ▼              │
                    │  Port Normalization    │
                    │          │              │
                    │          ▼              │
                    │  ML Preprocessing      │
                    │          │              │
                    │          ▼              │
                    │  Random Forest Model   │
                    │          │              │
                    │          ▼              │
                    │  Prediction Response   │
                    └─────────────────────────┘
                                 │
                                 ▼
                         Botnet Probability
                         + Classification
                         + Confidence
```

The model-serving layer is intentionally separated from the API layer. This allows the classifier and its preprocessing implementation to be replaced without requiring changes to the presentation layer.

---

## Project Structure

```text
botsentinel-be/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and routes
│   ├── predictor.py         # Model loading and prediction logic
│   ├── preprocessing.py     # Network port normalization
│   └── schemas.py           # API request/response validation
│
├── models/
│   └── botsentinel_model.joblib
│                              # Trained scikit-learn pipeline
│
├── tests/
│   ├── __init__.py
│   └── test_api.py           # API and validation tests
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Technology Stack

| Component           | Technology    |
| ------------------- | ------------- |
| API framework       | FastAPI       |
| ASGI server         | Uvicorn       |
| Data processing     | Pandas        |
| Numerical computing | NumPy         |
| Machine learning    | scikit-learn  |
| Model serialization | Joblib        |
| Validation          | Pydantic      |
| Configuration       | python-dotenv |
| Testing             | Pytest        |
| Language            | Python 3.14   |

---

## Machine Learning Pipeline

BotSentinel was trained using flow-level network traffic from the **CTU-13 Botnet Dataset**.

The classification task is:

```text
Botnet       → 1
Normal       → 0
Background   → 0
```

The resulting model performs **Botnet vs Non-Botnet classification**.

### Input Features

The serving pipeline uses the following features:

```text
duration
protocol
source_port
direction
destination_port
connection_state
source_tos
destination_tos
total_packets
total_bytes
source_bytes
```

Raw source and destination IP addresses are intentionally excluded from the model input to reduce dependence on environment-specific identifiers and potential memorization.

Scenario identifiers, timestamps, and the original traffic labels are also excluded from inference features.

### Preprocessing

The model pipeline performs:

1. Network port normalization
2. Missing-value imputation
3. Numerical feature standardization
4. Categorical feature encoding
5. Random Forest classification

Port values may appear in either decimal or hexadecimal representation in the CTU-13 data. BotSentinel normalizes both representations before inference.

Unknown categorical values are handled using the fitted preprocessing pipeline.

---

## Model Evaluation

The final Random Forest model was evaluated using a **scenario-aware holdout**, with Scenario 9 excluded from model training and used as an unseen evaluation scenario.

This was chosen to provide a stronger test of generalization than relying exclusively on a random train/test split.

### Held-Out Scenario 9 Results

| Metric               | Result |
| -------------------- | -----: |
| Accuracy             |    98% |
| ROC-AUC              | 0.9997 |
| PR-AUC               | 0.9998 |
| Botnet Precision     |   1.00 |
| Botnet Recall        |   0.97 |
| Botnet F1            |   0.99 |
| Non-Botnet Precision |   0.94 |
| Non-Botnet Recall    |   1.00 |
| Non-Botnet F1        |   0.97 |

### Confusion Matrix

```text
                  Predicted
                Non-Botnet  Botnet

Actual
Non-Botnet        18,139       31
Botnet             1,164   40,345
```

On the held-out scenario, the model produced:

* **31 false positives**
* **1,164 false negatives**
* **18,139 true negatives**
* **40,345 true positives**

These results represent performance on the sampled CTU-13 evaluation data and should not be interpreted as production-level performance on modern network traffic.

---

## Feature Analysis

Impurity-based feature importance from the Random Forest indicated that several network-flow characteristics contributed strongly to the classifier's decisions.

The most influential features included:

```text
source_port
duration
destination_port
source_bytes
direction
total_bytes
total_packets
protocol
```

Feature importance indicates how the trained model used features internally; it does **not** establish that an individual feature is causally responsible for botnet activity.

---

## API

### Base URL

When running locally:

```text
http://127.0.0.1:8000
```

### `GET /`

Returns basic service information.

Example response:

```json
{
  "name": "BotSentinel API",
  "status": "online",
  "version": "1.0.0"
}
```

### `GET /health`

Health-check endpoint used to verify that the API and model are available.

Example response:

```json
{
  "status": "healthy",
  "model": "loaded"
}
```

### `POST /predict`

Classifies a network traffic flow.

Example request:

```json
{
  "duration": 12.4,
  "protocol": "tcp",
  "source_port": "0x1F90",
  "direction": "->",
  "destination_port": 443,
  "connection_state": "S",
  "source_tos": 0,
  "destination_tos": 0,
  "total_packets": 15,
  "total_bytes": 1820,
  "source_bytes": 940
}
```

Example response:

```json
{
  "prediction": "Non-Botnet",
  "is_botnet": false,
  "botnet_probability": 0.065,
  "confidence": 0.935
}
```

The API returns:

| Field                | Description                                            |
| -------------------- | ------------------------------------------------------ |
| `prediction`         | `Botnet` or `Non-Botnet`                               |
| `is_botnet`          | Boolean classification                                 |
| `botnet_probability` | Model probability for the Botnet class                 |
| `confidence`         | Confidence associated with the returned classification |

---

## Validation and Security

Security was considered throughout the backend implementation rather than added only after development.

### Input Validation

Pydantic schemas enforce constraints such as:

* Non-negative durations
* Non-negative packet and byte counts
* Non-negative traffic statistics
* Maximum lengths for categorical string fields
* Valid numeric types

Invalid requests are rejected with HTTP `422`.

### CORS

Cross-origin requests are restricted to the configured frontend origin:

```text
FRONTEND_URL
```

The frontend URL is supplied through an environment variable rather than hardcoded into the application.

### Environment Configuration

Local configuration is stored in `.env`:

```env
FRONTEND_URL=https://botsentinel-fe.vercel.app
```

The `.env` file is excluded from version control.

### Logging

Prediction events are logged for operational visibility, including:

* Request client information
* Prediction result
* Prediction confidence

Submitted network-flow feature values are not written to application logs.

### Model Loading

The serialized scikit-learn model is loaded only from the trusted project model artifact.

Serialized Python objects such as Joblib files should only be loaded from trusted sources because deserialization can execute arbitrary code.

### Error Handling

Prediction failures are logged internally while the API returns a generic error message to the client rather than exposing implementation details.

---

## Local Development

### 1. Clone the repository

```bash
git clone <repository-url>
cd botsentinel-be
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
FRONTEND_URL=http://localhost:3000
```

For the deployed frontend, use its production origin instead.

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available through FastAPI at:

```text
http://127.0.0.1:8000/docs
```

---

## Testing

The project uses Pytest for API and validation testing.

Run:

```bash
pytest -v
```

The test suite covers:

* Root endpoint availability
* Health endpoint availability
* Valid prediction requests
* Negative numeric-value rejection
* Invalid type rejection
* Hexadecimal port handling
* Prediction response validation

The current test suite contains **7 passing tests**.

---

## Deployment

The backend is designed to run as a standard FastAPI application behind an ASGI server.

Production deployment requires:

```env
FRONTEND_URL=https://botsentinel-fe.vercel.app
```

The production server should bind to all network interfaces and use the platform-provided port:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The `/health` endpoint can be used as the deployment health check.

---

## Relationship to the Frontend

BotSentinel consists of two primary components:

```text
BotSentinel Frontend
Next.js
     │
     │ POST /predict
     ▼
BotSentinel Backend
FastAPI
     │
     ▼
Machine Learning Pipeline
     │
     ▼
Botnet / Non-Botnet Prediction
```

The frontend communicates with the backend using the `NEXT_PUBLIC_API_URL` environment variable.

The backend does not contain presentation-layer logic, keeping the ML inference service independently deployable.

---

## Dataset

The model was developed using the **CTU-13 Botnet Dataset**, a network traffic dataset containing captures of botnet, normal, and background traffic.

Dataset reference:

> García, S., Grill, M., Stiborek, J., & Zunino, A. (2014). An empirical comparison of botnet detection methods. *Computers & Security, 45*, 100–123.

The project uses extracted network-flow information rather than requiring the full raw packet captures during API inference.

---

## Limitations

BotSentinel is an academic ML/security prototype and has several important limitations:

* CTU-13 represents traffic captured in 2011 and may not reflect current network behavior.
* Offline evaluation does not guarantee performance on real-world production traffic.
* The classifier can learn patterns specific to the dataset and its collection environment.
* Network ports and other flow characteristics may contribute to environment-specific behavior.
* The evaluation dataset is not a substitute for continuous validation against modern traffic.
* The current API accepts flow features and does not perform packet capture or PCAP parsing directly.
* The model should not be treated as a standalone intrusion-prevention mechanism.

---

## Future Improvements

Potential future development includes:

* Real-time packet/flow ingestion
* Direct PCAP analysis
* Streaming detection
* Model monitoring and drift detection
* Explainable AI for individual predictions
* Additional modern network datasets
* Threshold tuning for different security objectives
* Model versioning and automated retraining
* Authentication and authorization for production API access
* Rate limiting and abuse protection
* Containerized deployment
* Automated CI/CD testing
* Security and performance monitoring

---

## Project Goals

BotSentinel was developed to demonstrate the integration of:

* Machine learning
* Network security
* Secure software development
* Backend engineering
* API design
* Data preprocessing
* Model evaluation
* Security-focused testing
* Deployment and system architecture

The project intentionally combines ML experimentation with software engineering practices so that the trained model can be exposed through a maintainable and testable application rather than remaining only as a research notebook.

---

## Status

**Current status:** Working prototype

* [x] Dataset exploration
* [x] Feature engineering
* [x] Model training
* [x] Scenario-aware evaluation
* [x] Model serialization
* [x] FastAPI inference service
* [x] Request validation
* [x] Security hardening
* [x] API tests
* [x] Frontend integration architecture
* [ ] Production deployment
* [ ] Real-time traffic ingestion
* [ ] Model monitoring
