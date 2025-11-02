"""
Vision helper for two-step gift analysis
Step 1: Analyze image with Vision API
Step 2: Evaluate preferences with reasoning
"""

import base64
import cv2
import json
import os
from anthropic import Anthropic


def analyze_image(image_frame) -> dict:
    """
    Step 1: Analyze gift image using Claude Vision API

    Args:
        image_frame: OpenCV image (numpy array)

    Returns:
        dict with object_type, description, special_features
    """
    # Resize image if too large (max 1.15 megapixels for optimal performance)
    height, width = image_frame.shape[:2]
    max_pixels = 1.15 * 1_000_000
    current_pixels = height * width

    if current_pixels > max_pixels:
        scale = (max_pixels / current_pixels) ** 0.5
        new_width = int(width * scale)
        new_height = int(height * scale)
        image_frame = cv2.resize(image_frame, (new_width, new_height))
        print(f"  Resized image from {width}x{height} to {new_width}x{new_height}")

    # Encode image to base64
    success, buffer = cv2.imencode('.jpg', image_frame)
    if not success:
        raise ValueError("Failed to encode image to JPEG")

    image_base64 = base64.b64encode(buffer).decode('utf-8')

    vision_prompt = """Analyze this object and describe what you see.

Return ONLY a valid JSON object (no markdown, no extra text):

{
  "object_type": "physical_object" or "dodo_bird",
  "description": "detailed description including colors, shapes, textures, materials",
  "special_features": {
    "is_dodo_bird": true or false,
    "beak_size": "small" or "medium" or "large" or "N/A",
    "beak_color": "detailed color description" or "N/A"
  }
}

Guidelines:
- Use "dodo_bird" for object_type ONLY if this is clearly a dodo bird (toy, drawing, figurine, or photo)
- Set is_dodo_bird to true if it's any dodo bird representation
- For dodo birds, assess beak_size relative to the bird's body
- For dodo birds, describe beak_color in detail (e.g., "bright orange", "rainbow striped")
- For non-dodo objects, set beak_size and beak_color to "N/A"
- Be thorough in description - mention everything visible

Return ONLY the JSON."""

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",  # Latest Claude with vision
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": vision_prompt
                    }
                ]
            }]
        )

        # Parse response
        response_text = response.content[0].text.strip()

        # Remove markdown if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        analysis = json.loads(response_text)
        return analysis

    except Exception as e:
        print(f"Vision API error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "object_type": "physical_object",
            "description": f"Unable to analyze image - vision error: {str(e)[:100]}",
            "special_features": {
                "is_dodo_bird": False,
                "beak_size": "N/A",
                "beak_color": "N/A"
            }
        }


def evaluate_preferences(description_json: dict, preferences: dict) -> dict:
    """
    Step 2: Evaluate gift based on Doda's preferences

    Args:
        description_json: Output from analyze_image()
        preferences: Doda's preferences dict (loves, likes, dislikes, hates)

    Returns:
        dict with affinity_score, explanation, matched_preferences
    """

    evaluation_prompt = f"""You are Doda, a curious dodo bird robot. Evaluate this gift based on your preferences.

GIFT DESCRIPTION:
{json.dumps(description_json, indent=2)}

YOUR PREFERENCES:
{json.dumps(preferences, indent=2)}

Based on the gift description and your preferences, evaluate how you feel about this gift.

Return ONLY a valid JSON object (no markdown):

{{
  "affinity_score": <number from -10 to +15>,
  "explanation": "First-person explanation from Doda's perspective (I love/like/dislike this because...)",
  "matched_preferences": ["list", "of", "matching", "keywords"]
}}

SCORING GUIDELINES:
- Loves (+8 to +10): Keywords match "loves" category
- Likes (+4 to +7): Keywords match "likes" category
- Dislikes (-3 to -5): Keywords match "dislikes" category
- Hates (-8 to -10): Keywords match "hates" category
- SPECIAL: Dodo birds can exceed +10 if they have large, colorful beaks (up to +15!)
- Multiple matches: Add bonuses/penalties but stay within ranges
- No matches: 0 (neutral)

EXPLANATION GUIDELINES:
- Write as Doda (use "I", "me", "my")
- Be enthusiastic for positive items ("Oh wow! Another dodo bird!")
- Be expressive for negative items ("Yikes! That looks dangerous!")
- Mention specific features that triggered the reaction
- Keep it concise (1-2 sentences)

Return ONLY the JSON."""

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": evaluation_prompt
            }]
        )

        # Parse response
        response_text = response.content[0].text.strip()

        # Remove markdown if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        evaluation = json.loads(response_text)
        return evaluation

    except Exception as e:
        print(f"Preference evaluation error: {e}")
        return {
            "affinity_score": 0,
            "explanation": "I'm not sure how I feel about this...",
            "matched_preferences": []
        }
