"""Basic tests for AgentTrace."""

import pytest
import tempfile
import os
from pathlib import Path

from agenttrace import traced, trace_event
from agenttrace.db import RunRecorder, init_db


def test_traced_decorator():
    """Test that the traced decorator works."""
    
    @traced
    def simple_function(x, y):
        return x + y
    
    result = simple_function(2, 3)
    assert result == 5


def test_trace_event():
    """Test trace_event logging."""
    
    @traced
    def function_with_events():
        trace_event("start", {"status": "beginning"})
        trace_event("middle", {"progress": 50})
        trace_event("end", {"status": "complete"})
        return "done"
    
    result = function_with_events()
    assert result == "done"


def test_run_recorder():
    """Test RunRecorder context manager."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        # Initialize DB
        init_db(db_path)
        
        # Create a run
        with RunRecorder("test_function", db_path=db_path) as recorder:
            recorder.log_step("test_step", '{"data": "test"}')
        
        # Verify DB was created
        assert db_path.exists()


def test_nested_traced_functions():
    """Test nested traced functions."""
    
    @traced
    def inner_function(x):
        trace_event("inner_processing", {"value": x})
        return x * 2
    
    @traced
    def outer_function(x):
        trace_event("outer_start", {"input": x})
        result = inner_function(x)
        trace_event("outer_end", {"result": result})
        return result
    
    result = outer_function(5)
    assert result == 10


def test_exception_handling():
    """Test that exceptions are properly propagated."""
    
    @traced
    def failing_function():
        trace_event("about_to_fail", {})
        raise ValueError("Test error")
    
    with pytest.raises(ValueError, match="Test error"):
        failing_function()


if __name__ == "__main__":
    # Run basic smoke test
    test_traced_decorator()
    test_trace_event()
    test_run_recorder()
    test_nested_traced_functions()
    print("✅ All tests passed!") 