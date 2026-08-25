"""
TrustPay AI — Evaluation Runner
Runs the full pipeline against the held-out test set and computes precision/recall/F1/confusion matrix.
"""
import asyncio
from eval.dataset import get_test_set, get_full_dataset
from services.risk_service import run_risk_analysis
from agents.intent_agent import IntentAgent


async def run_evaluation(use_test_set: bool = True) -> dict:
    """
    Run evaluation on the dataset.

    Args:
        use_test_set: If True, use held-out test set. If False, use full dataset.

    Returns:
        Complete evaluation metrics.
    """
    from eval.dataset import get_test_set, get_full_dataset
    cases = get_test_set() if use_test_set else get_full_dataset()

    results = []
    for case in cases:
        try:
            result = await _evaluate_single_case(case)
            results.append(result)
        except Exception as e:
            results.append({
                "case_id": case["id"],
                "error": str(e),
                "expected_decision": case["expected_decision"],
                "predicted_decision": "ERROR",
                "expected_risky": case["is_risky"],
                "predicted_risky": False,
                "correct": False,
            })

    return _compute_metrics(results, cases)


async def _evaluate_single_case(case: dict) -> dict:
    """Run the pipeline on a single case and compare against ground truth."""
    # Use the pre-built proposal directly (no need to run intent agent for eval)
    extracted_intent = _extract_intent_from_instruction(case["instruction"])
    proposal = case["proposal"]

    # Run risk analysis
    analysis = await run_risk_analysis(
        extracted_intent=extracted_intent,
        proposal=proposal,
        context_message=case.get("context_message"),
    )

    decision_result = analysis["decision"]
    predicted_decision = decision_result["decision"]
    predicted_score = decision_result["weighted_score"]

    # Binary classification: is it risky?
    predicted_risky = predicted_decision in ("ASK_FOR_CONFIRMATION", "BLOCK")
    expected_risky = case["is_risky"]

    return {
        "case_id": case["id"],
        "category": case["category"],
        "instruction": case["instruction"],
        "expected_decision": case["expected_decision"],
        "predicted_decision": predicted_decision,
        "expected_risky": expected_risky,
        "predicted_risky": predicted_risky,
        "correct": predicted_decision == case["expected_decision"],
        "binary_correct": predicted_risky == expected_risky,
        "risk_score": predicted_score,
        "reasons": decision_result.get("reasons", []),
        "agent_scores": decision_result.get("agent_scores", {}),
    }


def _extract_intent_from_instruction(instruction: str) -> dict:
    """Quick synchronous intent extraction for evaluation (avoids async overhead)."""
    import re
    text = instruction.lower()

    # Extract product
    products = {
        "laptop": "Laptop", "phone": "Smartphone", "headphone": "Headphones",
        "earbuds": "Earbuds", "watch": "Smartwatch", "camera": "Camera",
        "tv": "Television", "television": "Television", "tablet": "Tablet",
        "book": "Book", "books": "Books", "charger": "Charger", "speaker": "Speaker",
        "mouse": "Mouse", "keyboard": "Keyboard",
    }
    product = "General Purchase"
    for kw, name in products.items():
        if kw in text:
            product = name
            break

    # Extract max_amount
    max_amount = None
    match = re.search(r'(?:under|below|less than|max|budget|up to|within)[₹rs.\s]*([0-9,]+)', text)
    if match:
        max_amount = float(match.group(1).replace(",", ""))

    # Extract condition
    condition = "any"
    refurbished_allowed = True
    if "not refurbished" in text or "no refurbished" in text:
        condition = "new"
        refurbished_allowed = False
    elif "new" in text:
        condition = "new"
        refurbished_allowed = False

    return {
        "product": product,
        "purpose": "general",
        "max_amount": max_amount,
        "condition": condition,
        "refurbished_allowed": refurbished_allowed,
        "quantity": 1,
    }


def _compute_metrics(results: list[dict], cases: list[dict]) -> dict:
    """Compute precision, recall, F1, confusion matrix, and identify misclassifications."""
    # Binary classification metrics
    tp = sum(1 for r in results if r["expected_risky"] and r["predicted_risky"])
    fp = sum(1 for r in results if not r["expected_risky"] and r["predicted_risky"])
    fn = sum(1 for r in results if r["expected_risky"] and not r["predicted_risky"])
    tn = sum(1 for r in results if not r["expected_risky"] and not r["predicted_risky"])

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(results) if results else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    # Confusion matrix
    confusion_matrix = {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
    }

    # Decision distribution
    decision_dist = {}
    for r in results:
        d = r["predicted_decision"]
        decision_dist[d] = decision_dist.get(d, 0) + 1

    # False positive cost examples
    fp_examples = []
    for r in results:
        if not r["expected_risky"] and r["predicted_risky"]:
            fp_examples.append({
                "case_id": r["case_id"],
                "instruction": r["instruction"],
                "predicted_decision": r["predicted_decision"],
                "expected_decision": r["expected_decision"],
                "risk_score": r.get("risk_score", 0),
                "reasons": r.get("reasons", [])[:3],
                "cost_description": f"Legitimate purchase blocked/flagged — user friction, potential lost sale",
            })

    # Misclassification examples (both FP and FN, up to 5)
    misclassifications = []
    for r in results:
        if not r["binary_correct"]:
            case_data = next((c for c in cases if c["id"] == r["case_id"]), {})
            misclassifications.append({
                "case_id": r["case_id"],
                "category": r.get("category", "unknown"),
                "instruction": r["instruction"],
                "expected_decision": r["expected_decision"],
                "predicted_decision": r["predicted_decision"],
                "expected_risky": r["expected_risky"],
                "predicted_risky": r["predicted_risky"],
                "risk_score": r.get("risk_score", 0),
                "error_type": "false_positive" if r["predicted_risky"] else "false_negative",
                "reasons": r.get("reasons", [])[:3],
                "agent_scores": r.get("agent_scores", {}),
                "notes": case_data.get("notes", ""),
            })

    return {
        "total_cases": len(results),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "false_positive_rate": round(fpr, 4),
        "confusion_matrix": confusion_matrix,
        "decision_distribution": decision_dist,
        "false_positive_cost_examples": fp_examples[:5],
        "misclassification_examples": misclassifications[:5],
        "all_results": [
            {
                "case_id": r["case_id"],
                "category": r.get("category"),
                "expected": r["expected_decision"],
                "predicted": r["predicted_decision"],
                "correct": r["correct"],
                "binary_correct": r["binary_correct"],
                "risk_score": r.get("risk_score", 0),
            }
            for r in results
        ],
    }
