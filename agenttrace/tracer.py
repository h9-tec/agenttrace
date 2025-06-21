import functools
import json
import subprocess
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .db import RunRecorder, _DEFAULT_PATH

# Thread-local storage for current run context
_context = threading.local()


def get_current_recorder() -> Optional[RunRecorder]:
    """Get the current RunRecorder if inside a traced function."""
    return getattr(_context, 'recorder', None)


def trace_event(event_type: str, data: Dict[str, Any]):
    """Log an event to the current trace if one is active."""
    recorder = get_current_recorder()
    if recorder:
        recorder.log_step(event_type, json.dumps(data))


def get_git_sha() -> str:
    """Get current git SHA or 'unknown'."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()[:8]
    except:
        pass
    return "unknown"


def traced(func: Callable) -> Callable:
    """Decorator to trace function execution and capture events."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a new recorder for this run
        recorder = RunRecorder(
            func_name=func.__name__,
            git_sha=get_git_sha()
        )
        
        # Store in thread-local context
        old_recorder = getattr(_context, 'recorder', None)
        _context.recorder = recorder
        
        try:
            with recorder:
                # Log function start
                trace_event("function_start", {
                    "args": str(args)[:100],  # Truncate for safety
                    "kwargs": str(kwargs)[:100]
                })
                
                # Execute the function
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log function end
                trace_event("function_end", {
                    "duration": duration,
                    "result_type": type(result).__name__
                })
                
                return result
        finally:
            # Restore previous context
            _context.recorder = old_recorder
    
    return wrapper


class LangChainCallbackHandler:
    """Callback handler for LangChain that logs to AgentTrace."""
    
    def __init__(self):
        self.run_id = str(uuid.uuid4())
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: list, **kwargs):
        trace_event("llm_start", {
            "model": serialized.get("name", "unknown"),
            "prompts": prompts[:2] if len(prompts) > 2 else prompts  # Limit for size
        })
    
    def on_llm_end(self, response, **kwargs):
        trace_event("llm_end", {
            "generations": len(response.generations) if hasattr(response, 'generations') else 0
        })
    
    def on_llm_error(self, error: Exception, **kwargs):
        trace_event("llm_error", {
            "error": str(error)
        })
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs):
        trace_event("chain_start", {
            "chain_type": serialized.get("name", "unknown"),
            "inputs": list(inputs.keys())
        })
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs):
        trace_event("chain_end", {
            "outputs": list(outputs.keys())
        })
    
    def on_chain_error(self, error: Exception, **kwargs):
        trace_event("chain_error", {
            "error": str(error)
        })
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        trace_event("tool_start", {
            "tool": serialized.get("name", "unknown"),
            "input": input_str[:100]  # Truncate
        })
    
    def on_tool_end(self, output: str, **kwargs):
        trace_event("tool_end", {
            "output": output[:100]  # Truncate
        })
    
    def on_tool_error(self, error: Exception, **kwargs):
        trace_event("tool_error", {
            "error": str(error)
        })
    
    def on_agent_action(self, action, **kwargs):
        trace_event("agent_action", {
            "tool": action.tool if hasattr(action, 'tool') else "unknown",
            "input": str(action.tool_input)[:100] if hasattr(action, 'tool_input') else ""
        })
    
    def on_agent_finish(self, finish, **kwargs):
        trace_event("agent_finish", {
            "output": str(finish.return_values)[:100] if hasattr(finish, 'return_values') else ""
        })


class CrewAICallbackHandler:
    """Callback handler for CrewAI that logs to AgentTrace."""
    
    def on_task_start(self, task: Any):
        trace_event("crewai_task_start", {
            "description": str(task.description)[:100] if hasattr(task, 'description') else "",
            "agent": str(task.agent.role) if hasattr(task, 'agent') and hasattr(task.agent, 'role') else "unknown"
        })
    
    def on_task_complete(self, task: Any, output: Any):
        trace_event("crewai_task_complete", {
            "output": str(output)[:100]
        })
    
    def on_agent_action(self, agent: Any, action: str, context: Dict[str, Any]):
        trace_event("crewai_agent_action", {
            "agent": str(agent.role) if hasattr(agent, 'role') else "unknown",
            "action": action,
            "context": str(context)[:100]
        })


@contextmanager
def trace_langchain():
    """Context manager to automatically trace LangChain operations."""
    from langchain.callbacks import CallbackManager
    
    handler = LangChainCallbackHandler()
    callback_manager = CallbackManager([handler])
    
    # This would need to be integrated with LangChain's global callback system
    # For now, users need to pass the handler manually
    yield handler


def get_viewer():
    """Return the path to the viewer HTML file."""
    viewer_path = Path(__file__).parent / "viewer.html"
    if not viewer_path.exists():
        # Create a basic viewer if it doesn't exist
        create_basic_viewer(viewer_path)
    return viewer_path


def create_basic_viewer(path: Path):
    """Create a basic HTML viewer."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>AgentTrace Viewer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .run { margin: 20px 0; padding: 10px; border: 1px solid #ccc; }
        .step { margin: 10px 20px; padding: 5px; background: #f5f5f5; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>AgentTrace Viewer</h1>
    <p>Run <code>agenttrace view</code> to see your traces.</p>
</body>
</html>"""
    path.write_text(html) 