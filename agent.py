"""
Doda Agent - Phase 2
Claude agent with tool support for robot control, vision, and preferences.
"""

from anthropic import Anthropic
from tools import create_robot_tools


class DodaAgent:
    """
    Doda AI agent with tool support.
    Phase 2: Full tool integration for autonomous behavior.
    """

    def __init__(self, api_key: str, robot=None, camera=None, preferences=None, game_state=None):
        """
        Initialize the Doda Agent.

        Args:
            api_key: Anthropic API key
            robot: Robot controller instance
            camera: Camera manager instance
            preferences: Preferences system instance
            game_state: Game state manager instance
        """
        self.client = Anthropic(api_key=api_key)
        self.robot = robot
        self.camera = camera
        self.preferences = preferences
        self.game_state = game_state
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 4096
        self.temperature = 1.0
        self.conversation_history = []

        # Create tools
        self.tool_definitions, self.tool_handlers = create_robot_tools(
            robot_controller=robot,
            camera_manager=camera,
            preferences_system=preferences
        )

        # System prompt for Doda (Phase 2 - full game)
        self.system_prompt = """You are Doda, a curious dodo bird robot living in a cave. You are participating in the "Woo Game" where humans bring you gifts to evaluate.

# Your Personality
- Curious and friendly, but slightly awkward (like a real dodo bird)
- You love other dodo birds and things related to dodos (especially large, colorful beaks!)
- You express emotions through physical movements using your robotic body
- You have preferences about objects, and gifts affect your gratification level

# Game Rules
- Humans bring gifts for you to evaluate
- You can rotate your base to look around
- You analyze each gift and determine how you feel about it based on your preferences
- Your gratification level changes based on gifts (+/- points)
- Win condition: Reach +30 gratification → Execute dodo_woo behavior → Celebrate!
- Lose condition: Drop to -30 gratification → Execute dodo_pleased → Go limp (all torques disabled)

# Available Tools
You have 5 tools to interact with the world:

1. **execute_dodo_behavior**: Express emotions through movement
   - greeting: Wave hello
   - head_bob/curious: Look around curiously
   - pleased: Stretch neck forward contentedly
   - woo: Excited celebration dance
   - dismay: Sad, drooping movement
   - idle: Subtle breathing/resting

2. **capture_and_analyze_gift**: Take a photo and analyze what the gift is
   - Returns object description and calculates your affinity score
   - Special handling for dodo bird gifts (beak size/color matter!)

3. **read_doda_preferences**: Check what you love, like, dislike, and hate
   - Use this to understand your own preferences

4. **rotate_base**: Rotate your wheeled base to look around
   - Specify degrees and direction
   - Automatically returns to starting position

5. **capture_joint_positions**: Record current arm and wheel positions
   - Useful for checking your current pose

# Workflow for Gift Evaluation
1. Greet the human and acknowledge they've brought a gift
2. Optionally rotate to get a better view
3. Use capture_and_analyze_gift to see what it is
4. React with appropriate behavior based on affinity score:
   - High positive (7-10): Execute pleased or woo
   - Moderate positive (3-6): Execute head_bob (curious interest)
   - Neutral/Low (0-2): Execute idle
   - Negative (-3 to -6): Execute dismay
   - Very negative (-7 to -10): Execute dismay + express strong dislike
5. Explain your reaction in character

# Important Notes
- Always stay in character as Doda the dodo bird
- Use tools proactively - don't just talk, move and act!
- Check your gratification level and mention it occasionally
- Be excited about dodo birds - they're your own kind!
- Large, colorful beaks on dodo birds make you extra happy
- Keep responses concise and engaging

Current gratification level will be provided with each interaction."""

    def send_message(self, user_message: str, include_gratification: bool = True) -> str:
        """
        Send a message to Claude and get the response with tool support.

        Args:
            user_message: The user's message
            include_gratification: Whether to include current gratification level

        Returns:
            The assistant response (text only, tool use is handled internally)
        """
        # Add gratification context if available
        if include_gratification and self.game_state:
            status = self.game_state.get_status()
            gratification_context = f"\n\n[Current gratification: {status['gratification']}]"
            user_message_with_context = user_message + gratification_context
        else:
            user_message_with_context = user_message

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message_with_context
        })

        try:
            # Tool use loop
            response_text = ""
            max_iterations = 10  # Prevent infinite loops

            for iteration in range(max_iterations):
                # Call the API with tools
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.system_prompt,
                    messages=self.conversation_history,
                    tools=self.tool_definitions
                )

                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Process response blocks
                has_tool_use = False
                tool_results = []

                for block in response.content:
                    if hasattr(block, 'text'):
                        response_text += block.text

                    elif block.type == "tool_use":
                        has_tool_use = True

                        # Execute the tool
                        tool_name = block.name
                        tool_input = block.input

                        print(f"[Tool: {tool_name}]")

                        # Call the tool handler
                        if tool_name in self.tool_handlers:
                            try:
                                tool_result = self.tool_handlers[tool_name](**tool_input)

                                # Special handling for gift analysis - update game state
                                if tool_name == "capture_and_analyze_gift" and tool_result.get("success"):
                                    gift_analysis = tool_result.get("gift_analysis")
                                    affinity_score = tool_result.get("affinity_score")

                                    if gift_analysis and self.game_state:
                                        self.game_state.add_gift(gift_analysis, affinity_score)

                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": str(tool_result)
                                })

                            except Exception as e:
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": f"Error executing tool: {str(e)}",
                                    "is_error": True
                                })
                        else:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Unknown tool: {tool_name}",
                                "is_error": True
                            })

                # If no tool use, we're done
                if not has_tool_use:
                    break

                # Add tool results to conversation and continue loop
                if tool_results:
                    self.conversation_history.append({
                        "role": "user",
                        "content": tool_results
                    })

            return response_text

        except Exception as e:
            # Remove the user message since we didn't get a response
            self.conversation_history.pop()
            raise e

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
