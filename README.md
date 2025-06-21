# AgentTrace 🔍

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AgentTrace** is a lightweight, open-source Python library for tracing and monitoring AI agents, including LangChain and CrewAI applications. It provides real-time visibility into your agent's execution, helping you debug, optimize, and understand complex AI workflows.

## 🌟 Key Features

- **🔗 Framework Support**: Native integrations for LangChain, CrewAI, and custom agents
- **📊 Real-time Visualization**: Web-based viewer for exploring agent execution traces
- **🎯 Zero-Config Setup**: Simple decorators for instant tracing
- **💾 Local Storage**: SQLite-based storage with no external dependencies
- **🧵 Thread-Safe**: Built for concurrent agent execution
- **🎨 Beautiful UI**: Clean, modern interface for trace exploration
- **🚀 Production Ready**: Lightweight and performant for production use

## 📦 Installation

```bash
pip install agenttrace
```

Or install from source:

```bash
git clone https://github.com/h9-tec/agenttrace.git
cd agenttrace
pip install -e .
```

## 🚀 Quick Start

### Basic Usage

```python
from agenttrace import traced

@traced
def my_agent_function():
    # Your agent logic here
    return "Hello from traced agent!"

# View traces
# python -m agenttrace view
# Open http://localhost:8000
```

### CrewAI Integration

```python
from agenttrace.integrations.crewai import trace_crew
from crewai import Agent, Task, Crew, Process

# Create your agents
researcher = Agent(
    role='Researcher',
    goal='Find accurate information',
    backstory='Expert researcher with years of experience'
)

writer = Agent(
    role='Writer',
    goal='Create engaging content',
    backstory='Professional writer skilled in technical content'
)

# Create tasks
research_task = Task(
    description='Research the latest AI trends',
    expected_output='Summary of key AI trends',
    agent=researcher
)

writing_task = Task(
    description='Write an article about the research',
    expected_output='Engaging article about AI trends',
    agent=writer
)

# Create and trace crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential
)

# Add tracing
traced_crew = trace_crew(crew)

# Execute with full tracing
result = traced_crew.kickoff()
```

### OpenRouter Integration

```python
from crewai import Agent, Task, Crew, LLM
from agenttrace.integrations.crewai import trace_crew

# Configure OpenRouter LLM
llm = LLM(
    model="openrouter/openai/gpt-3.5-turbo",
    api_key="your-openrouter-api-key",
    base_url="https://openrouter.ai/api/v1"
)

# Create agent with OpenRouter
agent = Agent(
    role='AI Expert',
    goal='Provide insights on AI topics',
    backstory='You are an AI expert',
    llm=llm
)

# Rest of the setup...
```

### Manual Tracing

```python
from agenttrace import trace_event

# Log custom events
trace_event("analysis_started", {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000
})

# Log results
trace_event("analysis_completed", {
    "tokens_used": 850,
    "cost": 0.025,
    "duration": 2.3
})
```

## 🎯 Core Concepts

### Traces
A trace represents a complete execution flow of your agent, including all function calls, LLM interactions, and custom events.

### Events
Events are individual points in your agent's execution. AgentTrace automatically captures:
- Function entry/exit
- LLM calls and responses
- Tool usage
- Errors and exceptions
- Custom events you define

### Sessions
Each run of your application creates a new session, making it easy to compare different executions.

## 🛠️ Configuration

### Environment Variables

```bash
# Set custom database location (optional)
export AGENTTRACE_DB_PATH="~/.myapp/traces.db"

# Set viewer port (optional)
export AGENTTRACE_PORT=8080
```

### Programmatic Configuration

```python
import agenttrace

# Configure before using
agenttrace.configure(
    db_path="./my_traces.db",
    auto_trace=True,
    capture_locals=False
)
```

## 📊 Viewing Traces

Start the web viewer:

```bash
python -m agenttrace view
```

Or programmatically:

```python
from agenttrace import start_viewer
start_viewer(port=8000)
```

Navigate to `http://localhost:8000` to explore your traces.

### Viewer Features

- **Timeline View**: See execution flow over time
- **Tree View**: Explore nested function calls
- **Event Details**: Inspect inputs, outputs, and metadata
- **Search & Filter**: Find specific traces quickly
- **Performance Metrics**: Identify bottlenecks

## 🔧 Advanced Usage

### Custom Trace Context

```python
from agenttrace import get_current_trace_id, set_trace_metadata

@traced
def process_document(doc):
    # Add metadata to current trace
    set_trace_metadata({
        "document_id": doc.id,
        "document_type": doc.type
    })
    
    # Get trace ID for correlation
    trace_id = get_current_trace_id()
    logger.info(f"Processing document {doc.id} in trace {trace_id}")
```

### Selective Tracing

```python
from agenttrace import traced

# Trace only specific functions
@traced(capture_args=True, capture_result=True)
def important_function(x, y):
    return x + y

# Skip tracing in production
@traced(enabled=os.getenv("ENABLE_TRACING", "false") == "true")
def conditional_function():
    pass
```

### Integration Patterns

```python
# Trace LangChain agents
from langchain.agents import AgentExecutor
from agenttrace.integrations.langchain import trace_langchain

traced_agent = trace_langchain(agent_executor)

# Trace custom frameworks
from agenttrace import TraceMixin

class MyAgent(TraceMixin):
    def process(self, input_data):
        with self.trace_context("processing"):
            # Your logic here
            pass
```

## 🏗️ Architecture

AgentTrace is designed to be lightweight and non-intrusive:

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   Your App  │────▶│  AgentTrace  │────▶│  SQLite DB │
└─────────────┘     └──────────────┘     └────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  Web Viewer  │
                    └──────────────┘
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/h9-tec/agenttrace.git
cd agenttrace

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 agenttrace/
black agenttrace/
```

## 📄 License

AgentTrace is released under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with ❤️ by the AI community
- Inspired by tools like LangSmith and Weights & Biases
- Special thanks to all contributors

## 🔗 Links

- [Documentation](https://github.com/h9-tec/agenttrace)
- [PyPI Package](https://pypi.org/project/agenttrace)
- [GitHub Repository](https://github.com/h9-tec/agenttrace)
- [Issue Tracker](https://github.com/h9-tec/agenttrace/issues)

---

**Need help?** Open an issue or reach out on [Discord](https://discord.gg/agenttrace)

**Love AgentTrace?** Give us a ⭐ on GitHub! 