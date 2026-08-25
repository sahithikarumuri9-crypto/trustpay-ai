 # TrustPay AI 🛡️💳

## Agentic Payment Safety & Risk Management System

TrustPay AI is an **AI-powered multi-agent risk-decision system** designed to make AI-assisted commerce and payment transactions safer.

As AI agents increasingly help users search for products and initiate payments, there is an important question:

> **Does this payment actually match what the user intended, and is the payment context safe?**

TrustPay AI acts as a safety layer between an AI commerce agent and a payment system. It uses **LLM-based intent extraction and reasoning combined with deterministic policy guardrails** to analyze payment risks before execution.

---

## 🎯 Problem Statement

AI-powered commerce agents can automatically recommend products and initiate payments. However, a payment may be risky even when it is technically valid.

For example:

* A product may exceed the user's authorized budget.
* The proposed product may not match the user's original requirements.
* A payment request may contain scam patterns such as urgency or threats.
* A transaction may be significantly different from the user's normal spending behavior.

Traditional payment systems primarily focus on whether a transaction is technically valid. **TrustPay AI focuses on whether the transaction is safe and aligned with user intent.**

---

## 💡 Our Solution

TrustPay AI uses a visible **multi-agent workflow** to analyze a payment before it is executed:

**UNDERSTAND → OBSERVE → ANALYZE → REASON → DECIDE → ACT → MONITOR**

The system analyzes two major types of risk:

### 1. Intent Risk

Checks whether the proposed payment matches what the user originally requested.

Examples:

* Budget exceeded
* Wrong product
* Wrong product condition
* Other violated user constraints

### 2. Context and Scam Risk

Analyzes the surrounding payment message for suspicious patterns such as:

* Urgency
* Threats
* Impersonation
* Fake support messages
* Scam-like language

---

# 🤖 Multi-Agent Architecture

TrustPay AI consists of the following agents:

### 🧠 1. Intent Agent

Converts the user's natural language request into structured payment constraints.

**Example Input:**

> "Buy a laptop for college under ₹60,000. It must be new, not refurbished."

**Extracted Intent:**

```json
{
  "product": "Laptop",
  "purpose": "college",
  "max_amount": 60000,
  "condition": "new",
  "refurbished_allowed": false,
  "quantity": 1
}
```

---

### 🔍 2. Intent Verification Agent

Compares the proposed payment with the user's original intent.

It checks for:

* Budget violations
* Product mismatches
* Condition mismatches
* Other constraint violations

It produces an **intent risk score from 0–100** along with the violated constraints.

---

### 🚨 3. Context / Scam Detection Agent

Analyzes the payment context for suspicious or scam-like patterns.

Examples include:

* "Pay immediately or your account will be blocked!"
* Threats of service disconnection
* Fake authority or support messages
* High-pressure urgency

It outputs:

* Scam probability
* Detected patterns
* Risk score

---

### 📊 4. Behavior Anomaly Agent

Compares the current transaction with the user's historical spending behavior.

For example:

> Typical transaction range: ₹500–₹5,000
> Current transaction: ₹45,000

The system identifies this as an unusual transaction and increases the risk level.

---

### ⚖️ 5. Decision Agent

Combines the results from all risk agents and generates the final decision.

The default weighted scoring system is:

| Risk Agent          | Weight |
| ------------------- | -----: |
| Intent Verification |    40% |
| Scam Detection      |    30% |
| Behavior Anomaly    |    30% |

The Decision Agent can return:

| Risk Score | Decision                |
| ---------- | ----------------------- |
| 0–30       | ✅ ALLOW                 |
| 31–60      | ⚠️ WARN                 |
| 61–80      | 🤔 ASK_FOR_CONFIRMATION |
| 81–100     | 🚫 BLOCK                |

### Override Rules

Certain high-risk situations can override the weighted score:

* High scam probability can directly force a **BLOCK**
* Significant budget violations can require **human confirmation**
* A severe signal from an individual agent can increase the minimum decision severity

---

### ✅ 6. Post-Payment Verification Agent

After a simulated payment is executed, the system verifies that the final payment still matches the approved transaction.

It checks:

* Amount
* Merchant
* Product
* Payment status

This helps detect any mismatch or drift after approval.

---

# 🔄 System Workflow

```text
User Payment Request
        │
        ▼
   Intent Agent
        │
        ▼
Structured User Intent
        │
        ▼
Simulated Payment Proposal
        │
        ▼
 ┌──────────────────────────────┐
 │      Risk Analysis Agents    │
 │                              │
 │ • Intent Verification        │
 │ • Scam Detection             │
 │ • Behavior Anomaly           │
 └──────────────┬───────────────┘
                │
                ▼
          Decision Agent
                │
       ┌────────┼─────────┐
       ▼        ▼         ▼
     ALLOW    CONFIRM    BLOCK
                │
                ▼
       Human Confirmation
                │
                ▼
       Mock Payment Execution
                │
                ▼
     Post-Payment Verification
```

---

# ✨ Key Features

* 🤖 Multi-agent payment risk analysis
* 🧠 LLM-based natural language intent extraction
* 🔍 Intent-to-payment verification
* 🚨 Scam and suspicious context detection
* 📊 User behavior anomaly detection
* ⚖️ Weighted risk-based decision making
* 👤 Human-in-the-loop confirmation for medium-risk payments
* 💳 Mock payment execution — **no real money involved**
* ✅ Post-payment verification
* 📈 Evaluation dashboard with precision, recall, F1 score, and confusion matrix
* 🔎 Explainable AI decisions with reasons and evidence
* 🗂️ Transaction history and agent execution logs
* 🎮 Pre-built demo scenarios

---

# 🔎 Explainable Decisions

TrustPay AI does not produce a decision without an explanation.

Every risk decision includes information such as:

```text
BLOCKED because:

1. Payment exceeds the authorized budget.
2. Payment context contains high-risk urgency language.
3. Transaction amount is significantly higher than normal user behavior.

Final Risk Score: 91/100 — HIGH RISK
```

The goal is to help users understand:

> **"Why was this payment allowed, warned about, or blocked?"**

---

# 🎮 Demo Scenarios

The project includes five demo scenarios:

### 1. ✅ Safe Payment

**User:** "Buy headphones under ₹5,000"

A payment within the authorized budget should be allowed.

**Expected:** `ALLOW`

---

### 2. 💰 Budget Violation

**User:** "Buy a laptop under ₹60,000"

The proposed payment exceeds the user's budget.

**Expected:** `ASK_FOR_CONFIRMATION` or higher risk action depending on the analysis.

---

### 3. 🚨 Scam Context

A payment request contains a threat such as:

> "Your electricity will be disconnected today unless you pay now."

The transaction may appear normal, but the context is suspicious.

**Expected:** `BLOCK`

---

### 4. 📈 Unusual Behavior

The user's normal transactions are between ₹500–₹5,000, but the current transaction is significantly higher.

**Expected:** `ASK_FOR_CONFIRMATION`

---

### 5. ⚠️ Ambiguous Edge Case

An urgent but potentially legitimate situation is included to demonstrate that the system can have difficult cases and possible false positives.

This scenario helps evaluate the system honestly instead of showing only perfect examples.

---

# 📊 Evaluation and Metrics

TrustPay AI includes an evaluation pipeline that runs the risk analysis system against a labeled dataset.

The evaluation calculates:

* **Precision**
* **Recall**
* **F1 Score**
* **Accuracy**
* **False Positive Rate**
* **Confusion Matrix**

For binary evaluation:

* **Risky:** `ASK_FOR_CONFIRMATION` or `BLOCK`
* **Not Risky:** Lower-risk decisions

The system also identifies **false positives** and highlights their real-world cost, such as:

> A legitimate payment being unnecessarily blocked can cause user friction and potential loss of a sale.

This evaluation-first approach helps demonstrate the actual performance and limitations of the system.

> 📌 **Note:** Evaluation results should be generated from the running application rather than manually claimed in the README. This ensures the reported metrics remain honest and reproducible.

---

# 🛠️ Tech Stack

| Technology                 | Usage                 |
| -------------------------- | --------------------- |
| **Python**                 | Backend development   |
| **FastAPI**                | REST API framework    |
| **SQLAlchemy**             | Database ORM          |
| **SQLite**                 | Local database        |
| **Pydantic**               | Data validation       |
| **Gemini API**             | Optional LLM provider |
| **Mock LLM Provider**      | Offline fallback      |
| **HTML, CSS & JavaScript** | Frontend dashboard    |

---

# 📁 Project Structure

```text
TrustPay-AI/
│
└── backend/
    │
    ├── agents/
    │   ├── intent_agent.py
    │   ├── intent_verification_agent.py
    │   ├── scam_detection_agent.py
    │   ├── behavior_anomaly_agent.py
    │   ├── decision_agent.py
    │   └── post_payment_agent.py
    │
    ├── llm/
    │   ├── base.py
    │   ├── factory.py
    │   ├── gemini_provider.py
    │   └── mock_provider.py
    │
    ├── services/
    │   ├── payment_service.py
    │   └── risk_service.py
    │
    ├── routes/
    │   ├── intent.py
    │   ├── payment.py
    │   ├── risk.py
    │   ├── transactions.py
    │   ├── demo.py
    │   └── eval.py
    │
    ├── eval/
    │   ├── dataset.py
    │   └── runner.py
    │
    ├── static/
    │   ├── index.html
    │   ├── style.css
    │   └── app.js
    │
    ├── main.py
    ├── config.py
    ├── database.py
    ├── models.py
    ├── schemas.py
    └── requirements.txt
```

---

# 🚀 Getting Started

## Prerequisites

Make sure you have installed:

* Python 3.10 or later
* pip

---

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
```

Navigate to the backend folder:

```bash
cd YOUR-REPOSITORY/backend
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables (Optional)

The application supports an optional Gemini LLM provider.

Create a `.env` file inside the `backend` directory:

```env
GEMINI_API_KEY=your_api_key_here
LLM_PROVIDER=auto
```

### Running Without an API Key

No API key is required to run the basic project.

TrustPay AI includes a **mock LLM provider fallback**, allowing the application to run locally even when a Gemini API key is not configured.

---

## 5. Run the Application

```bash
uvicorn main:app --reload
```

Open your browser and visit:

```text
http://127.0.0.1:8000
```

---

# 🔌 API Endpoints

| Method | Endpoint                 | Description                             |
| ------ | ------------------------ | --------------------------------------- |
| POST   | `/api/intent/analyze`    | Extract user payment intent             |
| POST   | `/api/payment/propose`   | Generate a simulated payment proposal   |
| POST   | `/api/risk/analyze`      | Run the multi-agent risk analysis       |
| POST   | `/api/payment/execute`   | Execute a mock payment                  |
| POST   | `/api/payment/verify`    | Verify the completed payment            |
| GET    | `/api/transactions`      | View transaction history                |
| GET    | `/api/demo/scenarios`    | View available demo scenarios           |
| GET    | `/api/eval/metrics`      | Run evaluation on the held-out test set |
| GET    | `/api/eval/metrics/full` | Run evaluation on the full dataset      |
| GET    | `/health`                | Application health check                |

---

# 🧪 Example Use Case

### User Intent

> "Buy a laptop under ₹60,000. It must be new."

### Proposed Payment

```text
Product: Laptop
Merchant: ABC Electronics
Total Amount: ₹64,497
Condition: New
```

### TrustPay AI Analysis

The system checks:

* ❌ Payment exceeds the authorized budget
* ✅ Product matches the requested category
* ⚠️ Transaction may be unusual compared to historical behavior
* 🔍 No suspicious context detected

### Final Decision

```text
ASK_FOR_CONFIRMATION
```

The user can review the reasons and decide whether to proceed with the simulated payment.

---

# 🔒 Important Disclaimer

⚠️ **TrustPay AI is a Buildathon MVP and research prototype.**

* It does **not** process real payments.
* Payment execution is simulated.
* Synthetic user behavior and evaluation data are used for demonstration.
* The system is not intended to replace production fraud detection or regulatory compliance systems.

Before real-world deployment, the system would require real transaction data, security testing, privacy safeguards, fraud validation, regulatory compliance, and extensive production monitoring.

---

# 🔮 Future Improvements

Potential future enhancements include:

* Merchant Risk Agent
* Duplicate Payment Detection Agent
* Real payment gateway sandbox integration
* More advanced behavioral profiling
* Larger and more diverse evaluation datasets
* Authentication and user accounts
* Configurable risk thresholds and agent weights
* Advanced monitoring and production analytics

---

# 🏆 Why TrustPay AI?

TrustPay AI focuses on a gap that traditional payment validation alone does not solve:

> **A payment can be technically valid but still be unsafe or different from what the user actually intended.**

By combining **intent verification, scam context analysis, behavior anomaly detection, explainable decision-making, and human confirmation**, TrustPay AI aims to make AI-assisted payments more trustworthy and user-centric.

---

## 👩‍💻 Built For

**AI Risk Management / FinTech Buildathon**

### TrustPay AI — *Think Before You Pay. Verify Before You Trust.* 🛡️💳
