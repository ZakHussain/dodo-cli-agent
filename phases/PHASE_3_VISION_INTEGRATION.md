# Phase 3: Vision Integration - Two-Step Analysis

## Overview

Replace mock vision data with real Claude Vision API using a **two-step process**:
1. **Vision Analysis**: Analyze image → structured description
2. **Preference Evaluation**: Analyze description + preferences → affinity score + explanation

## Current State (Phase 2)

The `capture_and_analyze_gift` tool returns mock data. We need real vision + preference reasoning.

## Two-Step Architecture

### Step 1: Image Analysis (Vision API)
**Input**: Captured camera frame
**Process**: Claude Vision analyzes the image
**Output**: Structured JSON description

```json
{
  "object_type": "physical_object" | "dodo_bird",
  "description": "detailed description...",
  "special_features": {
    "is_dodo_bird": true/false,
    "beak_size": "small|medium|large|N/A",
    "beak_color": "color description|N/A"
  }
}
```

### Step 2: Preference Evaluation (Text API)
**Input**: Description JSON + Doda's preferences
**Process**: Claude reasons about how Doda would feel
**Output**: Affinity score + detailed explanation

```json
{
  "affinity_score": -10 to +15,
  "explanation": "I love this because...",
  "matched_preferences": ["dodo bird", "large beak", "colorful"]
}
```

## Implementation

### Create tools/vision_helper.py

```python
"""
Vision helper for two-step gift analysis
Step 1: Analyze image
Step 2: Evaluate preferences
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
    # Encode image to base64
    _, buffer = cv2.imencode('.jpg', image_frame)
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
            model="claude-3-5-sonnet-20241022",
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
        return {
            "object_type": "physical_object",
            "description": "Unable to analyze image - vision error",
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
```

### Update tools/robot_tools.py

Replace the mock section with two-step analysis:

```python
def handle_capture_gift(save_photo: bool = True) -> dict:
    """Capture and analyze gift using two-step vision process"""
    # Capture frame
    frame = camera_manager.capture_frame()

    if frame is None:
        return {
            "success": False,
            "error": "Failed to capture image from camera",
            "gift_analysis": None,
            "affinity_score": 0,
            "affinity_reason": ""
        }

    # Save photo if requested
    photo_path = None
    if save_photo:
        photo_dir = Path("game/gift_photos")
        photo_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        photo_path = photo_dir / f"gift_{timestamp}.jpg"

        camera_manager.save_frame(str(photo_path))

    # STEP 1: Analyze image with vision API
    from tools.vision_helper import analyze_image, evaluate_preferences

    print("  [Step 1/2] Analyzing image...")
    gift_analysis = analyze_image(frame)

    # STEP 2: Evaluate based on preferences
    print("  [Step 2/2] Evaluating preferences...")
    preferences = preferences_system.get_all_preferences()
    evaluation = evaluate_preferences(gift_analysis, preferences)

    affinity_score = evaluation["affinity_score"]
    affinity_reason = evaluation["explanation"]

    return {
        "success": True,
        "gift_analysis": gift_analysis,
        "affinity_score": affinity_score,
        "affinity_reason": affinity_reason,
        "matched_preferences": evaluation.get("matched_preferences", []),
        "photo_path": str(photo_path) if photo_path else None,
        "error": None
    }
```

## Benefits of Two-Step Approach

1. **Separation of Concerns**: Vision and reasoning are independent
2. **Better Reasoning**: Claude can see full preferences context when scoring
3. **Richer Explanations**: Doda's voice in the explanation (first-person)
4. **Flexibility**: Can test each step independently
5. **Extensibility**: Easy to add more evaluation criteria later

## Testing

```bash
python doda_terminal.py

> I have a gift for you
[Agent triggers capture_and_analyze_gift]
  [Step 1/2] Analyzing image...
  [Step 2/2] Evaluating preferences...
[Shows affinity score and Doda's explanation]

> /view-gift
[Manual test of both steps]
```

## Success Criteria

- ✅ Step 1 produces accurate image descriptions
- ✅ Step 2 produces reasonable affinity scores
- ✅ Doda's explanations are in-character and make sense
- ✅ Dodo bird detection works correctly
- ✅ Beak size/color bonuses apply properly
- ✅ Error handling prevents crashes

## Files to Create/Modify

1. **Create**: `tools/vision_helper.py` (two functions)
2. **Update**: `tools/robot_tools.py` (replace mock with two-step)
3. **Update**: `tools/__init__.py` (export vision helper)

Ready to implement?
