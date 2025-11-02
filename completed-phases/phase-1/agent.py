"""
Doda Agent - Phase 1
Simple Claude agent wrapper for conversation.
No tools yet - Phase 1 is just chat + manual behaviors.
"""

from anthropic import Anthropic


class DodaAgent:
    """
    Simple Claude agent for Doda Terminal.
    Phase 1: Basic conversation only, no tools.
    """

    def __init__(self, api_key: str, robot=None):
        """
        Initialize the Doda Agent.

        Args:
            api_key: Anthropic API key
            robot: Robot controller instance (not used in Phase 1)
        """
        self.client = Anthropic(api_key=api_key)
        self.robot = robot
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 4096
        self.temperature = 1.0
        self.conversation_history = []

        # System prompt for Doda (Phase 1 - minimal)
        self.system_prompt = """You are Doda, a curious dodo bird robot.

You are friendly, curious, and slightly awkward (like a real dodo). You live in a cave and are learning about the world.

In future phases, you'll be able to express emotions through physical movements, but for now you can only chat.

Keep responses concise and in-character. Show your dodo personality!"""

    def send_message(self, user_message: str) -> str:
        """
        Send a message to Claude and get the response.

        Args:
            user_message: The user's message

        Returns:
            The assistant response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            # Call the API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=self.conversation_history
            )

            # Extract text response
            assistant_message = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    assistant_message += block.text

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            # Remove the user message since we didn't get a response
            self.conversation_history.pop()
            raise e

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
