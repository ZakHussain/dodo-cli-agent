"""
Doda Terminal - Phase 1
Entry point for Doda the Agentic Dodo Robot Terminal

Phase 1: Foundation - Agent + Hardcoded Behavior
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich import box

# Initialize console
console = Console()

def print_welcome_banner():
    """Display welcome banner on startup."""
    banner = """
    🦤 [bold cyan]Doda Terminal[/bold cyan] [dim]Phase 1[/dim]

    Agentic Dodo Robot - Gift Evaluation Game
    Powered by [bold]Claude Sonnet 4[/bold]
    """

    panel = Panel(
        banner,
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 2)
    )
    console.print(panel)
    console.print("[yellow]Type /help for available commands | /exit to quit[/yellow]\n")


def print_system_message(message: str, msg_type: str = "info"):
    """Display system message with icon and color."""
    icons = {
        "info": "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error": "✗"
    }

    colors = {
        "info": "blue",
        "success": "green",
        "warning": "yellow",
        "error": "red"
    }

    icon = icons.get(msg_type, "ℹ")
    color = colors.get(msg_type, "white")

    console.print(f"[{color}]{icon} {message}[/{color}]")


def print_user_message(message: str):
    """Display user message in a cyan panel."""
    panel = Panel(
        message,
        title="You",
        title_align="left",
        border_style="cyan",
        box=box.ROUNDED
    )
    console.print(panel)


def print_assistant_message(message: str):
    """Display assistant message."""
    panel = Panel(
        message,
        title="Doda",
        title_align="left",
        border_style="white",
        box=box.ROUNDED
    )
    console.print(panel)


def print_help():
    """Display help message."""
    help_text = """[bold cyan]Available Commands (Phase 1)[/bold cyan]

[cyan]/help[/cyan]              Show this help message
[cyan]/behavior greeting[/cyan] Execute the greeting behavior on Doda
[cyan]/exit[/cyan]              Exit the terminal

[bold cyan]Chat:[/bold cyan]
Just type normally to chat with Doda (powered by Claude).

[bold]Phase 1 Features:[/bold]
• Chat with Doda
• Manual behavior execution (/behavior greeting)
• Basic terminal interface
    """

    panel = Panel(
        help_text,
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(panel)


def main():
    """Main entry point for Doda Terminal."""
    # Load environment variables
    load_dotenv()

    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print_system_message("Error: ANTHROPIC_API_KEY not found in environment variables.", "error")
        print_system_message("Please create a .env file with your API key:", "info")
        print_system_message("  ANTHROPIC_API_KEY=your_key_here", "info")
        sys.exit(1)

    # Import components
    try:
        from agent import DodaAgent
        from robot.controller import RobotController
    except ImportError as e:
        print_system_message(f"Error importing components: {e}", "error")
        print_system_message("Make sure all required files are present.", "error")
        sys.exit(1)

    # Initialize robot controller (lazy connection, uses local calibration file)
    robot = RobotController(port="COM7")

    # Initialize agent
    agent = DodaAgent(api_key=api_key, robot=robot)

    # Display welcome banner
    print_welcome_banner()

    # Main conversation loop
    try:
        while True:
            try:
                # Get user input
                user_input = console.input("[bold cyan]>[/bold cyan] ").strip()

            except EOFError:
                # Ctrl+D on empty line - exit
                console.print()
                print_system_message("Goodbye!", "success")
                break

            # Skip empty input
            if not user_input:
                continue

            console.print()  # Spacing

            # Check if it's a command
            if user_input.startswith('/'):
                cmd = user_input.lower()

                if cmd == "/exit" or cmd == "/quit":
                    print_system_message("Goodbye!", "success")
                    break

                elif cmd == "/help":
                    print_help()

                elif cmd == "/behavior greeting":
                    # Manual behavior execution
                    print_system_message("Executing greeting behavior...", "info")
                    try:
                        result = robot.execute_behavior("greeting")
                        if result["success"]:
                            print_system_message(f"Behavior executed successfully in {result['duration']:.1f}s", "success")
                        else:
                            print_system_message(f"Behavior failed: {result['error']}", "error")
                    except Exception as e:
                        print_system_message(f"Error: {e}", "error")

                else:
                    print_system_message(f"Unknown command: {user_input}", "error")
                    print_system_message("Type /help for available commands", "info")

            else:
                # Send to agent
                print_user_message(user_input)
                console.print()  # Spacing

                try:
                    response = agent.send_message(user_input)
                    print_assistant_message(response)
                except Exception as e:
                    print_system_message(f"Error communicating with agent: {e}", "error")

            console.print()  # Extra spacing between turns

    except KeyboardInterrupt:
        console.print()
        print_system_message("Goodbye!", "success")

    finally:
        # Cleanup
        robot.disconnect()


if __name__ == "__main__":
    main()
