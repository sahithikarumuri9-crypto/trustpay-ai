"""
TrustPay AI — Evaluation Routes
GET /api/eval/metrics
"""
from fastapi import APIRouter
from eval.runner import run_evaluation

router = APIRouter(prefix="/api/eval", tags=["Evaluation"])


@router.get("/metrics")
async def get_eval_metrics():
    """Run evaluation on the held-out test set and return precision/recall/F1/confusion matrix."""
    result = await run_evaluation(use_test_set=True)
    return result


@router.get("/metrics/full")
async def get_eval_metrics_full():
    """Run evaluation on the full dataset."""
    result = await run_evaluation(use_test_set=False)
    return result
