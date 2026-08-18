"""
ORION Agent Runtime Package
"""

from agents.runtime.provider import (
    AgentRunTrace,
    AgentRuntimeProvider,
    AgentTraceStep,
)
from agents.runtime.local_runtime import LocalAgentRuntime
from agents.runtime.adya_runtime import AdyaAgentRuntime, AdyaConnectionMode
from agents.runtime.config import get_configured_agent_runtime

# Global runtime singleton for the server
global_agent_runtime = get_configured_agent_runtime()

__all__ = [
    "AgentRunTrace",
    "AgentRuntimeProvider",
    "AgentTraceStep",
    "LocalAgentRuntime",
    "AdyaAgentRuntime",
    "AdyaConnectionMode",
    "get_configured_agent_runtime",
    "global_agent_runtime",
]
