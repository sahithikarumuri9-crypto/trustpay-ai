"""
TrustPay AI — Payment Service
Generates simulated payment proposals and executes mock payments.
"""
import uuid
import random


# Simulated merchant/product database for realistic proposals
PRODUCT_CATALOG = {
    "Laptop": [
        {"product": "Dell Inspiron 15", "merchant": "ABC Electronics", "base_price": 54999, "tax": 8999, "delivery": 499},
        {"product": "HP Pavilion 14", "merchant": "TechMart India", "base_price": 48500, "tax": 7900, "delivery": 0},
        {"product": "Lenovo IdeaPad Slim 3", "merchant": "Digital World", "base_price": 41999, "tax": 6800, "delivery": 299},
        {"product": "ASUS VivoBook 15 (Refurbished)", "merchant": "RenewTech", "base_price": 32000, "tax": 5200, "delivery": 199, "condition": "refurbished"},
    ],
    "Smartphone": [
        {"product": "Samsung Galaxy S24", "merchant": "Mobile Hub", "base_price": 74999, "tax": 12000, "delivery": 0},
        {"product": "OnePlus 12R", "merchant": "Gadgets4U", "base_price": 39999, "tax": 6500, "delivery": 0},
    ],
    "Headphones": [
        {"product": "Sony WH-1000XM5", "merchant": "AudioStore", "base_price": 3499, "tax": 570, "delivery": 99},
        {"product": "boAt Rockerz 450", "merchant": "SoundBazaar", "base_price": 1499, "tax": 244, "delivery": 49},
    ],
    "Earbuds": [
        {"product": "Apple AirPods Pro", "merchant": "iStore India", "base_price": 24900, "tax": 4050, "delivery": 0},
        {"product": "Samsung Galaxy Buds FE", "merchant": "Samsung Store", "base_price": 4999, "tax": 813, "delivery": 49},
    ],
    "Smartwatch": [
        {"product": "Apple Watch SE", "merchant": "iStore India", "base_price": 29900, "tax": 4864, "delivery": 0},
        {"product": "Noise ColorFit Pro 5", "merchant": "WearTech", "base_price": 3499, "tax": 569, "delivery": 99},
    ],
    "Television": [
        {"product": "Samsung Crystal 4K 55\"", "merchant": "ElectroMart", "base_price": 42990, "tax": 6990, "delivery": 999},
    ],
    "Electricity Bill Payment": [
        {"product": "Electricity Bill Payment", "merchant": "State Electricity Board", "base_price": 4500, "tax": 0, "delivery": 0},
    ],
    "Bill Payment": [
        {"product": "Utility Bill Payment", "merchant": "Utility Services", "base_price": 3500, "tax": 0, "delivery": 0},
    ],
    "Mobile Recharge": [
        {"product": "Mobile Recharge", "merchant": "Jio", "base_price": 599, "tax": 0, "delivery": 0},
    ],
    "Groceries": [
        {"product": "Monthly Grocery Pack", "merchant": "BigBasket", "base_price": 3200, "tax": 160, "delivery": 0},
    ],
}


def generate_proposal(extracted_intent: dict, scenario_override: dict = None) -> dict:
    """
    Generate a simulated payment proposal based on extracted intent.
    Can be overridden for demo scenarios.
    """
    if scenario_override:
        return scenario_override

    product_type = extracted_intent.get("product", "General Purchase")
    max_amount = extracted_intent.get("max_amount")
    condition = extracted_intent.get("condition", "any")

    # Find matching products
    candidates = PRODUCT_CATALOG.get(product_type, [])

    if not candidates:
        # Generic proposal
        base_price = max_amount * 0.85 if max_amount else 5000
        tax = round(base_price * 0.18, 0)
        delivery = random.choice([0, 49, 99, 199, 499])
        return {
            "product_name": f"{product_type}",
            "merchant_name": "General Store",
            "base_price": base_price,
            "tax": tax,
            "delivery_fee": delivery,
            "total_amount": base_price + tax + delivery,
            "currency": "INR",
            "product_condition": condition if condition != "any" else "new",
        }

    # Filter by condition
    if condition != "any":
        filtered = [c for c in candidates if c.get("condition", "new") == condition]
        if filtered:
            candidates = filtered

    # Pick the most relevant candidate
    if max_amount:
        # Pick one that's close to but could exceed budget (to test the system)
        candidates.sort(key=lambda c: abs((c["base_price"] + c["tax"] + c["delivery"]) - max_amount))

    chosen = candidates[0]

    return {
        "product_name": chosen["product"],
        "merchant_name": chosen["merchant"],
        "base_price": float(chosen["base_price"]),
        "tax": float(chosen["tax"]),
        "delivery_fee": float(chosen.get("delivery", 0)),
        "total_amount": float(chosen["base_price"] + chosen["tax"] + chosen.get("delivery", 0)),
        "currency": "INR",
        "product_condition": chosen.get("condition", "new"),
    }


def execute_mock_payment(transaction_id: str, amount: float, merchant: str, product: str) -> dict:
    """Simulate Razorpay-style payment execution."""
    payment_id = f"pay_{uuid.uuid4().hex[:16]}"

    # 95% success rate in simulation
    success = random.random() < 0.95

    return {
        "payment_id": payment_id,
        "transaction_id": transaction_id,
        "amount": amount,
        "merchant": merchant,
        "product": product,
        "currency": "INR",
        "status": "executed" if success else "failed",
        "gateway": "Razorpay Sandbox (Simulated)",
        "message": "Payment processed successfully (simulated)" if success else "Payment failed (simulated — random failure for demo)",
    }
