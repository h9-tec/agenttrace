import time
import random
from typing import Dict, Any

from .tracer import traced, trace_event, LangChainCallbackHandler


@traced
def simple_math_agent(question: str) -> str:
    """A simple demo agent that solves math problems."""
    trace_event("agent_thinking", {"question": question})
    
    # Simulate thinking
    time.sleep(0.5)
    
    # Parse the question
    if "+" in question:
        # Extract numbers from the question
        import re
        numbers = re.findall(r'\d+', question)
        if len(numbers) >= 2 and "+" in question:
            try:
                # Find the position of + and get numbers around it
                plus_pos = question.find("+")
                before_plus = question[:plus_pos]
                after_plus = question[plus_pos+1:]
                
                # Extract last number before + and first number after +
                nums_before = re.findall(r'\d+', before_plus)
                nums_after = re.findall(r'\d+', after_plus)
                
                if nums_before and nums_after:
                    a = int(nums_before[-1])
                    b = int(nums_after[0])
                    result = a + b
                    trace_event("calculation", {"a": a, "b": b, "operation": "add", "result": result})
                    return f"The answer is {result}"
            except (ValueError, IndexError):
                trace_event("parse_error", {"question": question})
                return "I couldn't parse that math question"
    
    trace_event("unsupported_operation", {"question": question})
    return "I can only handle addition for now"


@traced
def simulate_tool_use(tool_name: str, input_data: str) -> str:
    """Simulate using an external tool."""
    trace_event("tool_start", {"tool": tool_name, "input": input_data})
    
    # Simulate tool execution
    time.sleep(random.uniform(0.2, 0.8))
    
    if tool_name == "calculator":
        result = f"Result: {random.randint(1, 100)}"
    elif tool_name == "search":
        result = f"Found 3 results for '{input_data}'"
    else:
        result = "Unknown tool"
    
    trace_event("tool_end", {"tool": tool_name, "output": result})
    return result


@traced
def complex_agent_workflow(task: str) -> str:
    """A more complex agent that uses multiple tools."""
    trace_event("workflow_start", {"task": task})
    
    # Step 1: Analyze task
    trace_event("analyzing_task", {"task": task})
    time.sleep(0.3)
    
    # Step 2: Use search tool
    search_result = simulate_tool_use("search", task)
    
    # Step 3: Process results
    trace_event("processing_results", {"results": search_result})
    time.sleep(0.2)
    
    # Step 4: Use calculator
    calc_result = simulate_tool_use("calculator", "42 * 2")
    
    # Step 5: Generate response
    trace_event("generating_response", {})
    time.sleep(0.4)
    
    response = f"Based on my search ({search_result}) and calculations ({calc_result}), I've completed the task: {task}"
    
    trace_event("workflow_end", {"response": response})
    return response


def run_langchain_demo():
    """Demo using LangChain with AgentTrace."""
    try:
        from langchain.llms import FakeListLLM
        from langchain.agents import AgentType, initialize_agent, load_tools
        from langchain.callbacks import CallbackManager
    except ImportError:
        print("❌ LangChain not installed. Install with: pip install langchain")
        return
    
    @traced
    def langchain_agent_demo():
        # Create a fake LLM for demo purposes
        responses = [
            "I need to search for information about AI agents.",
            "I should calculate the cost of running 100 agents.",
            "Final Answer: AI agents are software programs that can act autonomously."
        ]
        llm = FakeListLLM(responses=responses)
        
        # Create callback handler
        callback_handler = LangChainCallbackHandler()
        callback_manager = CallbackManager([callback_handler])
        
        # Initialize agent with tools
        tools = []  # We'll use no real tools for the demo
        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            callback_manager=callback_manager,
            verbose=True
        )
        
        # Run the agent
        result = agent.run("What are AI agents and how much would it cost to run 100 of them?")
        return result
    
    result = langchain_agent_demo()
    print(f"\n✅ LangChain demo completed: {result}")


def run_simple_demo():
    """Run simple demonstration agents."""
    print("\n=== Running Simple Demo ===\n")
    
    # Demo 1: Simple math
    print("1. Simple Math Agent")
    result = simple_math_agent("What is 25 + 17?")
    print(f"   Result: {result}\n")
    
    # Demo 2: Complex workflow
    print("2. Complex Agent Workflow")
    result = complex_agent_workflow("Find the best AI frameworks and calculate their combined market share")
    print(f"   Result: {result}\n")
    
    # Demo 3: Error case
    print("3. Error Handling Demo")
    result = simple_math_agent("What is the meaning of life?")
    print(f"   Result: {result}\n")
    
    print("✅ Demo completed! Run 'agenttrace view' to see the traces.")


def run_demo(agent_type: str = "simple"):
    """Run the specified demo type."""
    if agent_type == "simple":
        run_simple_demo()
    elif agent_type == "langchain":
        run_langchain_demo()
    elif agent_type == "crewai":
        print("❌ CrewAI demo not implemented yet")
    else:
        print(f"❌ Unknown demo type: {agent_type}") 