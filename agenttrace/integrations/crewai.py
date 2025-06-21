"""CrewAI integration for AgentTrace.

This module provides comprehensive tracing for CrewAI agents, tasks, and crews.
"""

import json
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..tracer import trace_event, traced


class CrewAITracer:
    """Main tracer for CrewAI operations."""
    
    def __init__(self, trace_llm_calls: bool = True, trace_tools: bool = True):
        self.trace_llm_calls = trace_llm_calls
        self.trace_tools = trace_tools
        self.active_tasks = {}
        self.active_agents = {}
    
    def on_crew_start(self, crew: Any, inputs: Dict[str, Any]):
        """Called when a crew starts execution."""
        trace_event("crew_start", {
            "crew_id": id(crew),
            "agents": [agent.role for agent in crew.agents] if hasattr(crew, 'agents') else [],
            "tasks": len(crew.tasks) if hasattr(crew, 'tasks') else 0,
            "inputs": list(inputs.keys()) if inputs else []
        })
    
    def on_crew_end(self, crew: Any, output: Any):
        """Called when a crew finishes execution."""
        trace_event("crew_end", {
            "crew_id": id(crew),
            "output": str(output)[:500] if output else None,
            "success": True
        })
    
    def on_crew_error(self, crew: Any, error: Exception):
        """Called when a crew encounters an error."""
        trace_event("crew_error", {
            "crew_id": id(crew),
            "error": str(error),
            "error_type": type(error).__name__
        })
    
    def on_task_start(self, task: Any, agent: Any):
        """Called when a task starts."""
        task_id = id(task)
        self.active_tasks[task_id] = time.time()
        
        trace_event("task_start", {
            "task_id": task_id,
            "description": str(task.description)[:200] if hasattr(task, 'description') else "",
            "agent": agent.role if hasattr(agent, 'role') else str(agent),
            "expected_output": str(task.expected_output)[:100] if hasattr(task, 'expected_output') else None,
            "tools": [tool.name for tool in task.tools] if hasattr(task, 'tools') and task.tools else []
        })
    
    def on_task_end(self, task: Any, output: Any):
        """Called when a task completes."""
        task_id = id(task)
        duration = time.time() - self.active_tasks.get(task_id, time.time())
        
        trace_event("task_end", {
            "task_id": task_id,
            "output": str(output)[:500] if output else None,
            "duration": duration,
            "success": True
        })
        
        self.active_tasks.pop(task_id, None)
    
    def on_task_error(self, task: Any, error: Exception):
        """Called when a task fails."""
        task_id = id(task)
        
        trace_event("task_error", {
            "task_id": task_id,
            "error": str(error),
            "error_type": type(error).__name__
        })
        
        self.active_tasks.pop(task_id, None)
    
    def on_agent_action(self, agent: Any, action: str, thought: str = None):
        """Called when an agent takes an action."""
        agent_id = id(agent)
        
        trace_event("agent_action", {
            "agent_id": agent_id,
            "role": agent.role if hasattr(agent, 'role') else str(agent),
            "action": action,
            "thought": thought[:200] if thought else None,
            "goal": agent.goal if hasattr(agent, 'goal') else None
        })
    
    def on_tool_use(self, agent: Any, tool_name: str, tool_input: Any, tool_output: Any = None):
        """Called when an agent uses a tool."""
        if not self.trace_tools:
            return
            
        trace_event("tool_use", {
            "agent": agent.role if hasattr(agent, 'role') else str(agent),
            "tool": tool_name,
            "input": str(tool_input)[:200] if tool_input else None,
            "output": str(tool_output)[:200] if tool_output else None
        })
    
    def on_delegation(self, from_agent: Any, to_agent: Any, task: str):
        """Called when one agent delegates to another."""
        trace_event("delegation", {
            "from": from_agent.role if hasattr(from_agent, 'role') else str(from_agent),
            "to": to_agent.role if hasattr(to_agent, 'role') else str(to_agent),
            "task": task[:200]
        })


def create_traced_crew(crew_class):
    """Decorator to automatically trace a CrewAI Crew class."""
    
    class TracedCrew(crew_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._tracer = CrewAITracer()
        
        @traced
        def kickoff(self, inputs: Dict[str, Any] = None):
            self._tracer.on_crew_start(self, inputs)
            try:
                result = super().kickoff(inputs)
                self._tracer.on_crew_end(self, result)
                return result
            except Exception as e:
                self._tracer.on_crew_error(self, e)
                raise
    
    return TracedCrew


def create_traced_agent(agent_class):
    """Decorator to automatically trace a CrewAI Agent class."""
    
    class TracedAgent(agent_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._original_execute = self.execute
            self.execute = self._traced_execute
        
        @traced
        def _traced_execute(self, task: Any):
            trace_event("agent_execute", {
                "agent": self.role,
                "task": str(task)[:200]
            })
            return self._original_execute(task)
    
    return TracedAgent


def create_traced_task(task_class):
    """Decorator to automatically trace a CrewAI Task class."""
    
    class TracedTask(task_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._tracer = CrewAITracer()
        
        def execute(self, agent: Any):
            self._tracer.on_task_start(self, agent)
            try:
                result = super().execute(agent)
                self._tracer.on_task_end(self, result)
                return result
            except Exception as e:
                self._tracer.on_task_error(self, e)
                raise
    
    return TracedTask


# Convenience function for tracing existing CrewAI objects
def trace_crew(crew):
    """Add tracing to an existing Crew instance."""
    tracer = CrewAITracer()
    
    # Create a wrapper class that inherits from the crew's class
    class TracedCrewWrapper:
        def __init__(self, original_crew):
            self._original_crew = original_crew
            self._tracer = tracer
            # Copy all attributes from the original crew
            for attr in dir(original_crew):
                if not attr.startswith('_') and not callable(getattr(original_crew, attr)):
                    setattr(self, attr, getattr(original_crew, attr))
        
        def __getattr__(self, name):
            # Delegate attribute access to the original crew
            return getattr(self._original_crew, name)
        
        @traced
        def kickoff(self, inputs=None):
            self._tracer.on_crew_start(self._original_crew, inputs)
            try:
                result = self._original_crew.kickoff(inputs)
                self._tracer.on_crew_end(self._original_crew, result)
                return result
            except Exception as e:
                self._tracer.on_crew_error(self._original_crew, e)
                raise
        
        @traced
        def kickoff_async(self, inputs=None):
            self._tracer.on_crew_start(self._original_crew, inputs)
            try:
                result = self._original_crew.kickoff_async(inputs)
                self._tracer.on_crew_end(self._original_crew, result)
                return result
            except Exception as e:
                self._tracer.on_crew_error(self._original_crew, e)
                raise
    
    return TracedCrewWrapper(crew)


# Example callback for CrewAI's callback system
class AgentTraceCallback:
    """Callback handler that integrates with CrewAI's callback system."""
    
    def __init__(self):
        self.tracer = CrewAITracer()
    
    def on_task_start(self, task, agent):
        self.tracer.on_task_start(task, agent)
    
    def on_task_complete(self, task, output):
        self.tracer.on_task_end(task, output)
    
    def on_task_error(self, task, error):
        self.tracer.on_task_error(task, error)
    
    def on_agent_action(self, agent, action, thought=None):
        self.tracer.on_agent_action(agent, action, thought)
    
    def on_tool_use(self, agent, tool, tool_input, tool_output):
        self.tracer.on_tool_use(agent, tool, tool_input, tool_output) 