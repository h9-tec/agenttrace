"""AgentTrace - Lightweight observability for AI agents."""

__version__ = "0.1.0"

# Import core functionality
from .tracer import traced, trace_event, LangChainCallbackHandler, CrewAICallbackHandler

# Import viewer utilities
from .tracer import get_viewer

# Import CrewAI integrations (optional)
try:
    from .integrations.crewai import (
        create_traced_crew,
        create_traced_agent,
        trace_crew,
        AgentTraceCallback,
        CrewAITracer
    )
    _has_crewai_integration = True
except ImportError:
    _has_crewai_integration = False

__all__ = [
    "traced",
    "trace_event", 
    "get_viewer",
    "LangChainCallbackHandler",
    "CrewAICallbackHandler",
]

# Add CrewAI exports if available
if _has_crewai_integration:
    __all__.extend([
        "create_traced_crew",
        "create_traced_agent",
        "trace_crew",
        "AgentTraceCallback",
        "CrewAITracer"
    ]) 