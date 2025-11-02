"""
Doda Terminal - Phase 2
Entry point for Doda the Agentic Dodo Robot Terminal

Phase 2: Full Game - Agent with Tools + Win/Lose Conditions
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.text import Text

# Initialize console
console = Console()


def print_welcome_banner():
    """Display welcome banner on startup."""
    banner = """
    🦤 [bold cyan]Doda Terminal[/bold cyan] [dim]Phase 2[/dim]

    Gift Evaluation Game: WOO!
    Agentic Dodo Robot powered by [bold]Claude Sonnet 4[/bold]

    [yellow]Win:[/yellow] Reach +30 gratification → WOO!!
    [red]Lose:[/red] Drop to -30 gratification → Forever alone
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
        title="🦤 Doda",
        title_align="left",
        border_style="white",
        box=box.ROUNDED
    )
    console.print(panel)


def print_gratification_status(game_state):
    """Display current gratification level."""
    status = game_state.get_status()
    gratification = status["gratification"]

    # Color based on level
    if gratification >= 20:
        color = "bright_green"
    elif gratification >= 10:
        color = "green"
    elif gratification >= 0:
        color = "yellow"
    elif gratification >= -10:
        color = "orange1"
    else:
        color = "red"

    # Create progress bar
    bar_width = 30
    win_threshold = status["win_threshold"]
    lose_threshold = status["lose_threshold"]

    # Calculate position on bar (0-30)
    range_total = win_threshold - lose_threshold
    position = (gratification - lose_threshold) / range_total
    filled = int(position * bar_width)

    bar = "█" * max(0, filled) + "░" * max(0, bar_width - filled)

    text = f"[{color}]Gratification: {gratification:+d}[/{color}] [{bar}] [dim](Win: +{win_threshold} | Lose: {lose_threshold})[/dim]"
    console.print(text)


def print_win_screen():
    """Display win screen - WOO!!"""
    win_art = """
[bold bright_green]
╦ ╦╔═╗╔═╗  ╦  ╦
║║║║ ║║ ║  ║  ║
╚╩╝╚═╝╚═╝  ╚═╝╚═╝

DODA IS HAPPY!
[/bold bright_green]
    """

    panel = Panel(
        win_art,
        border_style="bright_green",
        box=box.DOUBLE_EDGE,
        padding=(2, 4)
    )
    console.print(panel)


def print_lose_screen():
    """Display lose screen - Forever Alone"""
    lose_art = """
[bold bright_red]
╔═╗╔═╗╦═╗╔═╗╦  ╦╔═╗╦═╗  ╔═╗╦  ╔═╗╔╗╔╔═╗
╠╣ ║ ║╠╦╝║╣ ╚╗╔╝║╣ ╠╦╝  ╠═╣║  ║ ║║║║║╣
╚  ╚═╝╩╚═╚═╝ ╚╝ ╚═╝╩╚═  ╩ ╩╩═╝╚═╝╝╚╝╚═╝

╦ ╦╔═╗╦ ╦  ╔═╗╦═╗╔═╗
╚╦╝║ ║║ ║  ╠═╣╠╦╝║╣
 ╩ ╚═╝╚═╝  ╩ ╩╩╚═╚═╝
[/bold bright_red]
    """

    panel = Panel(
        lose_art,
        border_style="bright_red",
        box=box.DOUBLE_EDGE,
        padding=(2, 4)
    )

    # Change console style to red background briefly
    console.print()
    console.print(panel)
    console.print()


def print_help():
    """Display help message."""
    help_text = """[bold cyan]Available Commands (Phase 2)[/bold cyan]

[cyan]/help[/cyan]              Show this help message
[cyan]/view-gift[/cyan]         Manually capture and analyze a gift
[cyan]/status[/cyan]            Show current gratification level
[cyan]/reset[/cyan]             Reset game state
[cyan]/exit[/cyan]              Exit the terminal

[bold cyan]Chat:[/bold cyan]
Just type normally to chat with Doda. Doda will use tools autonomously to:
- Execute physical behaviors
- Rotate to look around
- Analyze gifts when you present them
- Read preferences to understand likes/dislikes

[bold]Phase 2 Features:[/bold]
• Full agent autonomy with 5 tools
• Gratification-based game system
• Win condition: +30 gratification → WOO!!
• Lose condition: -30 gratification → Forever alone (robot goes limp)
• Camera-based gift analysis
• Preference system with affinity scoring
    """

    panel = Panel(
        help_text,
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(panel)


def handle_view_gift(agent, game_state):
    """Handle manual gift viewing command."""
    print_system_message("Capturing and analyzing gift...", "info")
    console.print()

    try:
        # Trigger agent with gift viewing prompt
        response = agent.send_message(
            "The human wants me to view the gift in front of me. I should use capture_and_analyze_gift."
        )

        print_assistant_message(response)
        console.print()

        # Show updated gratification
        print_gratification_status(game_state)

        # Check for win/lose
        status = game_state.get_status()
        return status["game_over"], status["won"]

    except Exception as e:
        print_system_message(f"Error: {e}", "error")
        return False, False


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
        from robot.camera import CameraManager
        from game import GameState
        from game.preferences import PreferencesSystem
    except ImportError as e:
        print_system_message(f"Error importing components: {e}", "error")
        print_system_message("Make sure all required files are present.", "error")
        sys.exit(1)

    # Initialize components
    print_system_message("Initializing Doda Terminal...", "info")

    # Robot controller (LeKiwi with calibration)
    robot = RobotController(port="COM8")  # COM8 for LeKiwi

    # Camera (index 1)
    camera = CameraManager(preferred_index=1)

    if not camera.is_connected():
        print_system_message("Warning: Camera not detected. Gift viewing will not work.", "warning")
        print_system_message("Connect camera and restart, or see /help for camera detection.", "info")

    # Game state
    game_state = GameState()

    # Preferences
    preferences = PreferencesSystem()

    # Agent with all systems
    agent = DodaAgent(
        api_key=api_key,
        robot=robot,
        camera=camera,
        preferences=preferences,
        game_state=game_state
    )

    print_system_message("Initialization complete!", "success")

    # Display welcome banner
    print_welcome_banner()

    # Show initial gratification
    print_gratification_status(game_state)
    console.print()

    # Main conversation loop
    try:
        while True:
            # Check if game is over
            status = game_state.get_status()
            if status["game_over"]:
                console.print()

                if status["won"]:
                    # Win sequence
                    print_system_message("Executing dodo_woo behavior...", "success")
                    robot.execute_behavior("woo")
                    print_win_screen()
                else:
                    # Lose sequence
                    print_system_message("Executing dodo_pleased behavior...", "warning")
                    robot.execute_behavior("pleased")
                    print_system_message("Disabling all torques... Doda goes limp", "warning")
                    robot.disable_all_torques()
                    print_lose_screen()

                console.print()
                print_system_message("Game over! Type /reset to play again or /exit to quit.", "info")

                # Wait for reset or exit
                while True:
                    try:
                        cmd = console.input("[bold cyan]>[/bold cyan] ").strip().lower()
                        if cmd == "/reset":
                            game_state.reset()
                            print_system_message("Game reset! Starting fresh...", "success")
                            print_gratification_status(game_state)
                            console.print()
                            break
                        elif cmd == "/exit":
                            print_system_message("Goodbye!", "success")
                            robot.disconnect()
                            return
                        else:
                            print_system_message("Game is over. Type /reset or /exit", "info")
                    except (EOFError, KeyboardInterrupt):
                        console.print()
                        print_system_message("Goodbye!", "success")
                        robot.disconnect()
                        return

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

                elif cmd == "/status":
                    print_gratification_status(game_state)

                elif cmd == "/reset":
                    game_state.reset()
                    print_system_message("Game reset! Starting fresh...", "success")
                    print_gratification_status(game_state)

                elif cmd == "/view-gift":
                    game_over, won = handle_view_gift(agent, game_state)
                    # Game over check happens at top of loop

                else:
                    print_system_message(f"Unknown command: {user_input}", "error")
                    print_system_message("Type /help for available commands", "info")

            else:
                # Send to agent
                print_user_message(user_input)
                console.print()

                try:
                    response = agent.send_message(user_input)
                    print_assistant_message(response)
                    console.print()

                    # Show gratification after agent response
                    print_gratification_status(game_state)

                except Exception as e:
                    print_system_message(f"Error communicating with agent: {e}", "error")
                    import traceback
                    traceback.print_exc()

            console.print()  # Extra spacing between turns

    except KeyboardInterrupt:
        console.print()
        print_system_message("Goodbye!", "success")

    finally:
        # Cleanup
        robot.disconnect()
        if camera:
            camera.disconnect()


if __name__ == "__main__":
    main()
