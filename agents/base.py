"""
TrustPay AI — Base Agent
Foundation class for all agents with logging and timing.
"""
import time
import uuid
from typing import Any


class BaseAgent:
    """Base class for all TrustPay risk agents."""

    AGENT_NAME: str = "base"
    AGENT_STEPS = ["UNDERSTAND", "OBSERVE", "ANALYZE", "REASON", "DECIDE"]

    def __init__(self):
        self.logs: list[dict] = []

    def _log(self, step: str, input_data: Any = None, output_data: Any = None, execution_time_ms: int = 0):
        """Record an agent step."""
        self.logs.append({
            "id": str(uuid.uuid4()),
            "agent_name": self.AGENT_NAME,
            "agent_step": step,
            "input_data": input_data,
            "output_data": output_data,
            "execution_time_ms": execution_time_ms,
        })

    async def run(self, **kwargs) -> dict:
        """Execute the agent pipeline. Override in subclasses."""
        self.logs = []
        start = time.time()
        result = await self._execute(**kwargs)
        elapsed = int((time.time() - start) * 1000)
        result["execution_time_ms"] = elapsed
        return result

    async def _execute(self, **kwargs) -> dict:
        """Override this in subclasses."""
        raise NotImplementedError

    def get_logs(self) -> list[dict]:
        return self.logs
