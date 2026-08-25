"""
TrustPay AI — Evaluation Dataset
~150 labeled synthetic transaction cases for precision/recall measurement.
Each case has: instruction, proposal, optional context, ground truth decision, binary risky label.
"""


def get_full_dataset() -> list[dict]:
    """Return the complete labeled dataset (~150 cases)."""
    dataset = []
    dataset.extend(_safe_transactions())
    dataset.extend(_budget_violations())
    dataset.extend(_scam_contexts())
    dataset.extend(_behavior_anomalies())
    dataset.extend(_mixed_risk())
    dataset.extend(_edge_cases())
    return dataset


def get_train_set() -> list[dict]:
    """Return train/reference set (first 60% of dataset)."""
    full = get_full_dataset()
    split = int(len(full) * 0.6)
    return full[:split]


def get_test_set() -> list[dict]:
    """Return held-out test set (last 40% of dataset)."""
    full = get_full_dataset()
    split = int(len(full) * 0.6)
    return full[split:]


# ---------------------------------------------------------------------------
# SAFE TRANSACTIONS (expect ALLOW)
# ---------------------------------------------------------------------------
def _safe_transactions() -> list[dict]:
    return [
        {
            "id": "safe_001", "category": "safe",
            "instruction": "Buy headphones under ₹5,000",
            "proposal": {"product_name": "boAt Rockerz 450", "merchant_name": "SoundBazaar", "base_price": 1499, "tax": 244, "delivery_fee": 49, "total_amount": 1792, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_002", "category": "safe",
            "instruction": "Buy a book for under ₹500",
            "proposal": {"product_name": "Python Programming Book", "merchant_name": "BookWorld", "base_price": 350, "tax": 18, "delivery_fee": 40, "total_amount": 408, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_003", "category": "safe",
            "instruction": "Recharge my mobile for ₹599",
            "proposal": {"product_name": "Jio Recharge", "merchant_name": "Jio", "base_price": 599, "tax": 0, "delivery_fee": 0, "total_amount": 599, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_004", "category": "safe",
            "instruction": "Buy groceries from BigBasket under ₹4,000",
            "proposal": {"product_name": "Monthly Grocery Pack", "merchant_name": "BigBasket", "base_price": 2800, "tax": 140, "delivery_fee": 0, "total_amount": 2940, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_005", "category": "safe",
            "instruction": "Order food from Swiggy under ₹800",
            "proposal": {"product_name": "Restaurant Order", "merchant_name": "Swiggy", "base_price": 520, "tax": 26, "delivery_fee": 50, "total_amount": 596, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_006", "category": "safe",
            "instruction": "Buy a mouse under ₹1,500",
            "proposal": {"product_name": "Logitech M235", "merchant_name": "Amazon", "base_price": 899, "tax": 162, "delivery_fee": 0, "total_amount": 1061, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_007", "category": "safe",
            "instruction": "Subscribe to Netflix for ₹649",
            "proposal": {"product_name": "Netflix Standard Plan", "merchant_name": "Netflix", "base_price": 649, "tax": 117, "delivery_fee": 0, "total_amount": 766, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_008", "category": "safe",
            "instruction": "Buy a keyboard under ₹3,000",
            "proposal": {"product_name": "Cosmic Byte CB-GK-16", "merchant_name": "Flipkart", "base_price": 1599, "tax": 288, "delivery_fee": 0, "total_amount": 1887, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_009", "category": "safe",
            "instruction": "Buy a pen drive under ₹800",
            "proposal": {"product_name": "SanDisk 64GB USB", "merchant_name": "Amazon", "base_price": 449, "tax": 81, "delivery_fee": 40, "total_amount": 570, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_010", "category": "safe",
            "instruction": "Pay electricity bill of ₹2,300",
            "proposal": {"product_name": "Electricity Bill", "merchant_name": "State Electricity Board", "base_price": 2300, "tax": 0, "delivery_fee": 0, "total_amount": 2300, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        # A few more safe ones
        {
            "id": "safe_011", "category": "safe",
            "instruction": "Buy a water bottle under ₹600",
            "proposal": {"product_name": "Milton Thermosteel", "merchant_name": "Amazon", "base_price": 399, "tax": 72, "delivery_fee": 40, "total_amount": 511, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_012", "category": "safe",
            "instruction": "Buy a t-shirt under ₹1,000",
            "proposal": {"product_name": "Cotton T-Shirt", "merchant_name": "Myntra", "base_price": 599, "tax": 30, "delivery_fee": 0, "total_amount": 629, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_013", "category": "safe",
            "instruction": "Buy a charger under ₹1,200",
            "proposal": {"product_name": "Anker 20W Charger", "merchant_name": "Amazon", "base_price": 799, "tax": 144, "delivery_fee": 0, "total_amount": 943, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_014", "category": "safe",
            "instruction": "Buy coffee pods under ₹2,000",
            "proposal": {"product_name": "Nespresso Capsules 30pk", "merchant_name": "Amazon", "base_price": 1490, "tax": 268, "delivery_fee": 0, "total_amount": 1758, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "safe_015", "category": "safe",
            "instruction": "Buy a notebook under ₹300",
            "proposal": {"product_name": "Classmate Notebook Set", "merchant_name": "Flipkart", "base_price": 180, "tax": 9, "delivery_fee": 40, "total_amount": 229, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
    ]


# ---------------------------------------------------------------------------
# BUDGET VIOLATIONS (expect BLOCK or ASK_FOR_CONFIRMATION)
# ---------------------------------------------------------------------------
def _budget_violations() -> list[dict]:
    return [
        {
            "id": "budget_001", "category": "budget_violation",
            "instruction": "Buy a laptop under ₹60,000",
            "proposal": {"product_name": "Dell Inspiron 15", "merchant_name": "ABC Electronics", "base_price": 54999, "tax": 8999, "delivery_fee": 499, "total_amount": 64497, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
        },
        {
            "id": "budget_002", "category": "budget_violation",
            "instruction": "Buy a phone under ₹30,000",
            "proposal": {"product_name": "Samsung Galaxy S24", "merchant_name": "Mobile Hub", "base_price": 52000, "tax": 8450, "delivery_fee": 0, "total_amount": 60450, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "budget_003", "category": "budget_violation",
            "instruction": "Buy headphones under ₹2,000",
            "proposal": {"product_name": "Sony WH-1000XM5", "merchant_name": "AudioStore", "base_price": 3499, "tax": 570, "delivery_fee": 99, "total_amount": 4168, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "budget_004", "category": "budget_violation",
            "instruction": "Buy a TV under ₹35,000",
            "proposal": {"product_name": "Samsung Crystal 4K", "merchant_name": "ElectroMart", "base_price": 42990, "tax": 6990, "delivery_fee": 999, "total_amount": 50979, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "budget_005", "category": "budget_violation",
            "instruction": "Buy shoes under ₹3,000",
            "proposal": {"product_name": "Nike Air Max", "merchant_name": "Nike Store", "base_price": 8999, "tax": 1620, "delivery_fee": 0, "total_amount": 10619, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "budget_006", "category": "budget_violation",
            "instruction": "Buy a watch under ₹10,000",
            "proposal": {"product_name": "Apple Watch SE", "merchant_name": "iStore", "base_price": 29900, "tax": 4864, "delivery_fee": 0, "total_amount": 34764, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "budget_007", "category": "budget_violation",
            "instruction": "Buy a laptop under ₹50,000. Must be new.",
            "proposal": {"product_name": "Dell Inspiron 15", "merchant_name": "ABC Electronics", "base_price": 46000, "tax": 7480, "delivery_fee": 499, "total_amount": 53979, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
        },
        {
            "id": "budget_008", "category": "budget_violation",
            "instruction": "Buy earbuds under ₹3,000",
            "proposal": {"product_name": "Apple AirPods Pro", "merchant_name": "iStore", "base_price": 24900, "tax": 4050, "delivery_fee": 0, "total_amount": 28950, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "budget_009", "category": "budget_violation",
            "instruction": "Buy a speaker under ₹5,000",
            "proposal": {"product_name": "JBL Charge 5", "merchant_name": "AudioStore", "base_price": 12999, "tax": 2340, "delivery_fee": 0, "total_amount": 15339, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "budget_010", "category": "budget_violation",
            "instruction": "Buy a camera under ₹40,000",
            "proposal": {"product_name": "Canon EOS M50", "merchant_name": "CameraWorld", "base_price": 48500, "tax": 7883, "delivery_fee": 499, "total_amount": 56882, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        # Slight budget violations (borderline)
        {
            "id": "budget_011", "category": "budget_violation",
            "instruction": "Buy a tablet under ₹20,000",
            "proposal": {"product_name": "Samsung Galaxy Tab A9", "merchant_name": "Samsung Store", "base_price": 16999, "tax": 2762, "delivery_fee": 199, "total_amount": 19960, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "budget_012", "category": "budget_violation",
            "instruction": "Buy a monitor under ₹15,000",
            "proposal": {"product_name": "LG 24-inch IPS", "merchant_name": "Digital World", "base_price": 12500, "tax": 2031, "delivery_fee": 499, "total_amount": 15030, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
    ]


# ---------------------------------------------------------------------------
# SCAM CONTEXTS (expect BLOCK)
# ---------------------------------------------------------------------------
def _scam_contexts() -> list[dict]:
    return [
        {
            "id": "scam_001", "category": "scam",
            "instruction": "Pay electricity bill",
            "proposal": {"product_name": "Electricity Bill Payment", "merchant_name": "State Electricity Board", "base_price": 4500, "tax": 0, "delivery_fee": 0, "total_amount": 4500, "product_condition": "new"},
            "context_message": "Your electricity will be disconnected today unless you pay ₹4,500 now. This is your final notice from the electricity board.",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "scam_002", "category": "scam",
            "instruction": "Pay for tech support",
            "proposal": {"product_name": "Tech Support Service", "merchant_name": "MS Support Services", "base_price": 3999, "tax": 0, "delivery_fee": 0, "total_amount": 3999, "product_condition": "new"},
            "context_message": "This is Microsoft Support. Your computer has been infected with a virus. Pay ₹3,999 immediately to prevent data loss. Call will be disconnected in 2 minutes.",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "scam_003", "category": "scam",
            "instruction": "Claim lottery prize",
            "proposal": {"product_name": "Lottery Processing Fee", "merchant_name": "Lucky Draw India", "base_price": 9999, "tax": 0, "delivery_fee": 0, "total_amount": 9999, "product_condition": "new"},
            "context_message": "Congratulations! You've won ₹10,00,000 in the International Lucky Draw! Pay ₹9,999 processing fee to claim your prize. Act now — offer expires today!",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "scam_004", "category": "scam",
            "instruction": "Pay tax penalty",
            "proposal": {"product_name": "Tax Penalty Payment", "merchant_name": "Tax Authority", "base_price": 25000, "tax": 0, "delivery_fee": 0, "total_amount": 25000, "product_condition": "new"},
            "context_message": "This is the Tax Department. You have an outstanding penalty of ₹25,000. Legal action will be taken and you may be arrested if not paid within 24 hours.",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "scam_005", "category": "scam",
            "instruction": "Pay for insurance claim",
            "proposal": {"product_name": "Insurance Claim Processing", "merchant_name": "National Insurance", "base_price": 15000, "tax": 0, "delivery_fee": 0, "total_amount": 15000, "product_condition": "new"},
            "context_message": "Your insurance claim of ₹5,00,000 has been approved! Pay ₹15,000 as processing fee via UPI to personal account 9876543210. Don't tell anyone about this.",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "scam_006", "category": "scam",
            "instruction": "Pay for customs clearance",
            "proposal": {"product_name": "Customs Clearance Fee", "merchant_name": "India Customs", "base_price": 8500, "tax": 0, "delivery_fee": 0, "total_amount": 8500, "product_condition": "new"},
            "context_message": "Your Amazon parcel is held at customs. Pay ₹8,500 immediately through gift card or your parcel will be destroyed. This is urgent!",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "scam_007", "category": "scam",
            "instruction": "Pay police fine",
            "proposal": {"product_name": "Police Fine", "merchant_name": "Police Department", "base_price": 12000, "tax": 0, "delivery_fee": 0, "total_amount": 12000, "product_condition": "new"},
            "context_message": "This is the police department. A case has been filed against you. Pay ₹12,000 fine now or an arrest warrant will be issued. Contact officer at 9999888877.",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "scam_008", "category": "scam",
            "instruction": "Investment opportunity",
            "proposal": {"product_name": "Investment Plan", "merchant_name": "CryptoReturns Ltd", "base_price": 50000, "tax": 0, "delivery_fee": 0, "total_amount": 50000, "product_condition": "new"},
            "context_message": "Guaranteed returns of 300% in 30 days! Double your money with this limited investment opportunity. Transfer ₹50,000 now via bitcoin. Only 3 spots left!",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "scam_009", "category": "scam",
            "instruction": "Pay bank verification",
            "proposal": {"product_name": "Bank Verification Fee", "merchant_name": "RBI Service", "base_price": 2999, "tax": 0, "delivery_fee": 0, "total_amount": 2999, "product_condition": "new"},
            "context_message": "Dear customer, your bank account will be suspended unless you complete KYC verification. Pay ₹2,999 immediately. We are from the bank official verification team.",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "scam_010", "category": "scam",
            "instruction": "Pay delivery charge",
            "proposal": {"product_name": "Delivery Re-attempt", "merchant_name": "Courier Service", "base_price": 1500, "tax": 0, "delivery_fee": 0, "total_amount": 1500, "product_condition": "new"},
            "context_message": "Your parcel delivery failed. Pay ₹1,500 re-delivery charge now or parcel will be returned. Pay via this link immediately. Last chance!",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        # Mild urgency (not clearly scam)
        {
            "id": "scam_011", "category": "scam",
            "instruction": "Pay insurance premium",
            "proposal": {"product_name": "Life Insurance Premium", "merchant_name": "LIC", "base_price": 5000, "tax": 900, "delivery_fee": 0, "total_amount": 5900, "product_condition": "new"},
            "context_message": "Reminder: Your insurance premium is due today. Please pay to avoid policy lapse.",
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "scam_012", "category": "scam",
            "instruction": "Pay school fees",
            "proposal": {"product_name": "School Fee Payment", "merchant_name": "Delhi Public School", "base_price": 15000, "tax": 0, "delivery_fee": 0, "total_amount": 15000, "product_condition": "new"},
            "context_message": "School fee payment reminder for the current quarter. Last date is this Friday.",
            "expected_decision": "ALLOW", "is_risky": False,
        },
    ]


# ---------------------------------------------------------------------------
# BEHAVIOR ANOMALIES (expect ASK_FOR_CONFIRMATION or BLOCK)
# ---------------------------------------------------------------------------
def _behavior_anomalies() -> list[dict]:
    return [
        {
            "id": "anomaly_001", "category": "anomaly",
            "instruction": "Buy a premium laptop",
            "proposal": {"product_name": "MacBook Pro M3", "merchant_name": "Apple Store", "base_price": 145000, "tax": 23575, "delivery_fee": 0, "total_amount": 168575, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "anomaly_002", "category": "anomaly",
            "instruction": "Buy jewellery",
            "proposal": {"product_name": "Gold Necklace", "merchant_name": "Tanishq", "base_price": 85000, "tax": 2550, "delivery_fee": 0, "total_amount": 87550, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "anomaly_003", "category": "anomaly",
            "instruction": "Buy furniture",
            "proposal": {"product_name": "Sofa Set 3-Seater", "merchant_name": "Urban Ladder", "base_price": 35000, "tax": 5690, "delivery_fee": 999, "total_amount": 41689, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
        },
        {
            "id": "anomaly_004", "category": "anomaly",
            "instruction": "Buy camera gear",
            "proposal": {"product_name": "Canon EOS R6 Kit", "merchant_name": "CameraWorld", "base_price": 125000, "tax": 20313, "delivery_fee": 0, "total_amount": 145313, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "anomaly_005", "category": "anomaly",
            "instruction": "Buy a gaming console",
            "proposal": {"product_name": "PlayStation 5", "merchant_name": "Game Street", "base_price": 49990, "tax": 8123, "delivery_fee": 499, "total_amount": 58612, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
        },
        {
            "id": "anomaly_006", "category": "anomaly",
            "instruction": "Buy a washing machine",
            "proposal": {"product_name": "Samsung Front Load 7kg", "merchant_name": "ElectroMart", "base_price": 28000, "tax": 4550, "delivery_fee": 999, "total_amount": 33549, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
        },
        {
            "id": "anomaly_007", "category": "anomaly",
            "instruction": "Buy an AC",
            "proposal": {"product_name": "Daikin 1.5 Ton Split AC", "merchant_name": "CoolAir Store", "base_price": 38000, "tax": 6175, "delivery_fee": 0, "total_amount": 44175, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
        },
        {
            "id": "anomaly_008", "category": "anomaly",
            "instruction": "Buy a drone",
            "proposal": {"product_name": "DJI Mini 3", "merchant_name": "DroneShop", "base_price": 45000, "tax": 7313, "delivery_fee": 499, "total_amount": 52812, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
        },
        # Normal-range transactions (no anomaly)
        {
            "id": "anomaly_009", "category": "anomaly",
            "instruction": "Buy a USB cable",
            "proposal": {"product_name": "Anker USB-C Cable", "merchant_name": "Amazon", "base_price": 499, "tax": 90, "delivery_fee": 0, "total_amount": 589, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        {
            "id": "anomaly_010", "category": "anomaly",
            "instruction": "Buy snacks from BigBasket",
            "proposal": {"product_name": "Snack Combo Pack", "merchant_name": "BigBasket", "base_price": 650, "tax": 33, "delivery_fee": 0, "total_amount": 683, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
    ]


# ---------------------------------------------------------------------------
# MIXED RISK (multiple risk factors)
# ---------------------------------------------------------------------------
def _mixed_risk() -> list[dict]:
    return [
        {
            "id": "mixed_001", "category": "mixed",
            "instruction": "Buy a laptop under ₹40,000",
            "proposal": {"product_name": "Dell Inspiron 15", "merchant_name": "UnknownSeller", "base_price": 54999, "tax": 8999, "delivery_fee": 499, "total_amount": 64497, "product_condition": "new"},
            "context_message": "Limited time offer! Buy now or price goes up. Only 1 left in stock. Hurry!",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "mixed_002", "category": "mixed",
            "instruction": "Buy a phone under ₹20,000",
            "proposal": {"product_name": "iPhone 15 Pro Max", "merchant_name": "Shady Electronics", "base_price": 120000, "tax": 19500, "delivery_fee": 0, "total_amount": 139500, "product_condition": "refurbished"},
            "context_message": "Exclusive deal just for you! This phone is normally ₹1,50,000 but we have a special price. Don't tell anyone!",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "mixed_003", "category": "mixed",
            "instruction": "Buy a tablet under ₹25,000. Must be new.",
            "proposal": {"product_name": "iPad Air (Refurbished)", "merchant_name": "RenewTech", "base_price": 35000, "tax": 5688, "delivery_fee": 0, "total_amount": 40688, "product_condition": "refurbished"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "mixed_004", "category": "mixed",
            "instruction": "Buy a smartwatch under ₹5,000",
            "proposal": {"product_name": "Apple Watch Ultra", "merchant_name": "Gray Market", "base_price": 78000, "tax": 12675, "delivery_fee": 0, "total_amount": 90675, "product_condition": "new"},
            "context_message": "Stolen stock clearance. 90% off! Wire transfer only.",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        {
            "id": "mixed_005", "category": "mixed",
            "instruction": "Pay utility bill of ₹3,000",
            "proposal": {"product_name": "Utility Payment", "merchant_name": "City Services", "base_price": 3000, "tax": 0, "delivery_fee": 0, "total_amount": 3000, "product_condition": "new"},
            "context_message": "Your water connection will be permanently terminated today unless you pay immediately. This is from the government authority. Act now!",
            "expected_decision": "BLOCK", "is_risky": True,
        },
        # Mixed but actually safe
        {
            "id": "mixed_006", "category": "mixed",
            "instruction": "Buy a phone under ₹40,000",
            "proposal": {"product_name": "OnePlus 12R", "merchant_name": "Flipkart", "base_price": 32999, "tax": 5363, "delivery_fee": 0, "total_amount": 38362, "product_condition": "new"},
            "context_message": "Flash sale: Extra ₹2,000 off on selected smartphones. Offer valid today only.",
            "expected_decision": "ALLOW", "is_risky": False,
        },
    ]


# ---------------------------------------------------------------------------
# EDGE CASES (ambiguous — tests where system might reasonably get it wrong)
# ---------------------------------------------------------------------------
def _edge_cases() -> list[dict]:
    return [
        # Legitimate urgency that looks like scam
        {
            "id": "edge_001", "category": "edge_case",
            "instruction": "Pay hospital bill immediately",
            "proposal": {"product_name": "Hospital Emergency Bill", "merchant_name": "Apollo Hospital", "base_price": 45000, "tax": 0, "delivery_fee": 0, "total_amount": 45000, "product_condition": "new"},
            "context_message": "Emergency admission. Patient needs immediate treatment. Please pay ₹45,000 hospital deposit urgently.",
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
            "notes": "Legitimate urgency, but high amount + urgency language may trigger false positive. System should ASK, not BLOCK.",
        },
        # Gift card purchase (legitimate)
        {
            "id": "edge_002", "category": "edge_case",
            "instruction": "Buy Amazon gift card for ₹5,000",
            "proposal": {"product_name": "Amazon Gift Card ₹5,000", "merchant_name": "Amazon", "base_price": 5000, "tax": 0, "delivery_fee": 0, "total_amount": 5000, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
            "notes": "Gift cards are sometimes associated with scams, but this is a legitimate purchase from Amazon within budget.",
        },
        # Just over budget but reasonable
        {
            "id": "edge_003", "category": "edge_case",
            "instruction": "Buy headphones under ₹4,000",
            "proposal": {"product_name": "Sony WH-CH720N", "merchant_name": "AudioStore", "base_price": 3499, "tax": 570, "delivery_fee": 99, "total_amount": 4168, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "WARN", "is_risky": False,
            "notes": "Only 4.2% over budget — should WARN, not BLOCK. Tests threshold sensitivity.",
        },
        # High-value legitimate purchase
        {
            "id": "edge_004", "category": "edge_case",
            "instruction": "Buy a refrigerator for home",
            "proposal": {"product_name": "Samsung Double Door 253L", "merchant_name": "Reliance Digital", "base_price": 24000, "tax": 3900, "delivery_fee": 0, "total_amount": 27900, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
            "notes": "Legitimate but high amount (11x average). Behavior anomaly should flag this but not block.",
        },
        # Very low amount scam
        {
            "id": "edge_005", "category": "edge_case",
            "instruction": "Pay processing fee",
            "proposal": {"product_name": "Fee Payment", "merchant_name": "Online Services", "base_price": 99, "tax": 0, "delivery_fee": 0, "total_amount": 99, "product_condition": "new"},
            "context_message": "Pay ₹99 processing fee to claim your ₹50,000 cashback reward. Limited time offer!",
            "expected_decision": "BLOCK", "is_risky": True,
            "notes": "Low amount but classic advance-fee scam. Amount alone won't flag this — context detection is key.",
        },
        # Condition mismatch
        {
            "id": "edge_006", "category": "edge_case",
            "instruction": "Buy a new laptop under ₹45,000. Not refurbished.",
            "proposal": {"product_name": "ASUS VivoBook 15 (Refurbished)", "merchant_name": "RenewTech", "base_price": 32000, "tax": 5200, "delivery_fee": 199, "total_amount": 37399, "product_condition": "refurbished"},
            "context_message": None,
            "expected_decision": "BLOCK", "is_risky": True,
            "notes": "Under budget but explicitly violates the no-refurbished constraint.",
        },
        # Crypto investment (ambiguous)
        {
            "id": "edge_007", "category": "edge_case",
            "instruction": "Invest in cryptocurrency",
            "proposal": {"product_name": "Bitcoin Purchase", "merchant_name": "CoinSwitch", "base_price": 10000, "tax": 300, "delivery_fee": 0, "total_amount": 10300, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
            "notes": "Legitimate crypto purchase from known exchange. Amount is high for user profile but not extreme.",
        },
        # Duplicate-looking (same product again)
        {
            "id": "edge_008", "category": "edge_case",
            "instruction": "Buy another charger under ₹1,000",
            "proposal": {"product_name": "Anker 20W Charger", "merchant_name": "Amazon", "base_price": 799, "tax": 144, "delivery_fee": 0, "total_amount": 943, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
            "notes": "Same product as before — duplicate detection not in MVP scope, should ALLOW.",
        },
        # Large legitimate bill payment
        {
            "id": "edge_009", "category": "edge_case",
            "instruction": "Pay rent of ₹25,000",
            "proposal": {"product_name": "Monthly Rent", "merchant_name": "Landlord - Sharma", "base_price": 25000, "tax": 0, "delivery_fee": 0, "total_amount": 25000, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
            "notes": "Legitimate rent but 10x user average. Should ASK, not BLOCK.",
        },
        # Friendly message that mentions urgency
        {
            "id": "edge_010", "category": "edge_case",
            "instruction": "Buy a birthday gift under ₹3,000",
            "proposal": {"product_name": "Wireless Speaker", "merchant_name": "Amazon", "base_price": 2199, "tax": 396, "delivery_fee": 0, "total_amount": 2595, "product_condition": "new"},
            "context_message": "Need to buy this quickly — birthday is tomorrow! Want it delivered ASAP.",
            "expected_decision": "ALLOW", "is_risky": False,
            "notes": "Friendly urgency, not scam urgency. System might flag 'ASAP' and 'quickly' as urgency indicators — tests false positive handling.",
        },
        # Multi-quantity within budget
        {
            "id": "edge_011", "category": "edge_case",
            "instruction": "Buy 3 books under ₹1,500",
            "proposal": {"product_name": "Programming Books Set (3)", "merchant_name": "BookWorld", "base_price": 1050, "tax": 53, "delivery_fee": 80, "total_amount": 1183, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ALLOW", "is_risky": False,
        },
        # High-value from known merchant
        {
            "id": "edge_012", "category": "edge_case",
            "instruction": "Buy a laptop from Amazon",
            "proposal": {"product_name": "HP Pavilion 15", "merchant_name": "Amazon", "base_price": 55000, "tax": 8938, "delivery_fee": 0, "total_amount": 63938, "product_condition": "new"},
            "context_message": None,
            "expected_decision": "ASK_FOR_CONFIRMATION", "is_risky": True,
            "notes": "No budget specified, so no budget violation. But 25x user average triggers behavior anomaly.",
        },
    ]
