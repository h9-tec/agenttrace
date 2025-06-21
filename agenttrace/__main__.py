import argparse
import sys
from pathlib import Path

from .viewer import start_viewer
from .demo import run_demo


def main():
    parser = argparse.ArgumentParser(
        description="AgentTrace - Observability for AI Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agenttrace demo         Run a demo agent with tracing
  agenttrace view         Open the trace viewer
  agenttrace view --port 8080  Start viewer on custom port
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run a demo agent with tracing')
    demo_parser.add_argument(
        '--agent', 
        choices=['simple', 'langchain', 'crewai'], 
        default='simple',
        help='Type of demo agent to run'
    )
    
    # View command
    view_parser = subparsers.add_parser('view', help='Open the trace viewer')
    view_parser.add_argument(
        '--port', 
        type=int, 
        default=8000,
        help='Port to run the viewer on (default: 8000)'
    )
    view_parser.add_argument(
        '--no-browser', 
        action='store_true',
        help="Don't open browser automatically"
    )
    
    args = parser.parse_args()
    
    if args.command == 'demo':
        print(f"🚀 Running {args.agent} demo...")
        run_demo(args.agent)
    elif args.command == 'view':
        print(f"🔍 Starting AgentTrace viewer on http://localhost:{args.port}")
        print("Press Ctrl+C to stop the server")
        try:
            start_viewer(port=args.port, open_browser=not args.no_browser)
        except KeyboardInterrupt:
            print("\n👋 Viewer stopped")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 