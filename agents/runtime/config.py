"""
ORION Agent Runtime Provider Configuration & Factory
"""

import os
from typing import Literal

from agents.runtime.provider import AgentRuntimeProvider
from agents.runtime.local_runtime import LocalAgentRuntime
from agents.runtime.adya_runtime import AdyaAgentRuntime, AdyaConnectionMode


def get_configured_agent_runtime(
    provider_name: Literal["local", "adya", "adya_simulated"] | None = None
) -> AgentRuntimeProvider:
    """
    Factory creating the active agent runtime provider based on configuration.
    Default: 'local' (deterministic LocalAgentRuntime).
    """
    selected = provider_name or os.getenv("ORION_AGENT_RUNTIME_PROVIDER", "local").lower()

    if selected == "adya" or selected == "adya_live":
        return AdyaAgentRuntime(connection_mode=AdyaConnectionMode.LIVE_ADYA_ENDPOINT)
    elif selected == "adya_simulated" or selected == "adya_sse":
        return AdyaAgentRuntime(connection_mode=AdyaConnectionMode.SIMULATED_SSE)
    else:
        return LocalAgentRuntime()
