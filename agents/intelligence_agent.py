import google.generativeai as genai
import os
import json
import logging
import random
from dotenv import load_dotenv

# Rich pool of simulated insights for variety
_TACTICAL_INSIGHTS = [
    "The batter is using the depth of the crease intelligently, giving extra time against the short-pitched delivery and using the bounce to place the ball through the square leg region.",
    "Excellent weight transfer on to the front foot — the batter has driven through the line of the ball, exploiting the full length delivery with a dominant cover drive.",
    "The batter has picked the slower ball early, adjusting hands at the last moment to guide the ball through the gap between deep cover and long-off.",
    "A cross-seam delivery aimed at the stumps forces the batter back, resulting in a controlled punch through mid-wicket to rotate the strike.",
    "The batter reads the swing and lets the outswinger go, showing great discipline at a critical stage of the innings."
]
_MATCH_CONTEXTS = [
    "In the {phase} phase with {wickets} wickets down, the team is balancing aggression with preservation. Every dot ball increases pressure exponentially.",
    "With {wickets} wickets in hand during the {phase}, the strategy shifts to maximizing run rate while ensuring the last recognized pair remains at the crease.",
    "At {wickets} wickets down in the {phase} overs, this is a match-defining moment. The bowling team will test the batter's temperament with pace variation.",
    "The {phase} phase demands smart cricket. At {wickets} down, partnerships are more valuable than explosive strokeplay.",
    "The scoreboard pressure in the {phase} with {wickets} wickets gone forces unorthodox shot selection — this is precisely when captains make aggressive field changes."
]
_NEXT_BALL_PREDICTIONS = [
    "Expect a slower delivery — possibly a knuckle ball — outside off stump. The bowler will aim to induce a false shot given the batter's aggressive intent.",
    "A back-of-a-length delivery angled into the body is likely. The bowler will try to cramp the batter and prevent the flowing drive.",
    "The bowler will come around the wicket with a fuller delivery targeting the stumps, eliminating the leg-side option entirely.",
    "Look for a well-disguised off-cutter. The bowler is unlikely to bowl the same line twice consecutively after that boundary.",
    "A yorker is imminent. The bowler has built up to full pace and the natural progression is to deliver a toe-crushing yorker at the death.",
    "A short-of-length ball outside off-stump — the bowler is setting up the batter for a slower ball trap in the following delivery."
]
_VISUAL_ANALYSES = [
    "The batter appears in a high-elbow, front-foot drive position with weight fully transferred forward. Excellent head position over the ball, suggesting confident strokeplay. The pitch shows signs of wear in the rough outside off stump.",
    "A clear backfoot punch shot is being executed. The batter's base is wide for balance, with the bat face angled to bisect the covers. The bowler's follow-through is visible in the background.",
    "The image captures a sweeping motion — the batter is down on one knee with the bat horizontal, aimed at the fine-leg boundary. The wicketkeeper is caught off-guard indicating a surprise shot selection.",
    "The defensive push is evident: the batter's hands are soft on the bat handle, head perfectly still over a front-foot stride. The ball appears to be in the off-stump corridor.",
    "An aggressive pull shot in full motion — the batter's upper body rotation is complete, with the bat finishing high. This suggests the short-pitched delivery was anticipated."
]

def _smart_simulate(event: dict, context: dict) -> dict:
    """Generate rich, context-aware simulated insights without the API."""
    phase = context.get('match_phase', 'middle')
    wickets = context.get('wickets', 3)
    runs = event.get('runs', 1)
    shot = event.get('shot', 'drive')

    pressure = "high" if phase == "death" or wickets >= 7 else ("medium" if phase == "middle" else "low")
    intent = "aggressive" if runs >= 4 or phase == "death" else ("defensive" if wickets >= 7 else "rotational")

    return {
        "visual_analysis": random.choice(_VISUAL_ANALYSES),
        "visual_stats": {
            "Aggression": random.randint(7, 10) if intent == "aggressive" else random.randint(3, 6),
            "Footwork": random.randint(6, 10),
            "Timing_Estimation": random.randint(6, 10),
            "Power": random.randint(6, 10) if runs >= 4 else random.randint(3, 7)
        },
        "shot_type": shot.capitalize(),
        "intent": intent.capitalize(),
        "pressure_level": pressure.capitalize(),
        "tactical_insight": random.choice(_TACTICAL_INSIGHTS),
        "match_context": random.choice(_MATCH_CONTEXTS).format(phase=phase, wickets=wickets),
        "next_ball_prediction": random.choice(_NEXT_BALL_PREDICTIONS),
        "simulated": True
    }


def generate_insights(image_path: str, event: dict, context: dict) -> dict:
    """
    Uses Gemini multimodal API to visually analyze the uploaded photo, generate intelligence,
    and predict the next ball. Falls back to rich simulation if the API is unavailable.
    """
    # Always reload .env so changes take effect without server restart
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        return _smart_simulate(event, context)

    # Try multiple model names for compatibility with different API key tiers
    models_to_try = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.0-pro-vision",
        "gemini-pro-vision",
    ]

    mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
    with open(image_path, "rb") as f:
        image_data = {"mime_type": mime_type, "data": f.read()}

    prompt = f"""
    You are an expert cricket analyst. I have provided an image of a cricket match.
    Please analyze the photo visually to understand what is happening.

    Also, factor in this real-time match context:
    {json.dumps(context, indent=2)}

    Based on the photo and the context, generate the following in strict JSON format:
    1. "visual_analysis": Detailed description of what you see (player positioning, posture, shot motion, pitch, lighting).
    2. "visual_stats": Dict with scores 0-10 for exactly these keys: "Aggression", "Footwork", "Timing_Estimation", "Power".
    3. "shot_type": The type of shot or action occurring.
    4. "intent": Batter's intent — "aggressive", "defensive", or "rotational".
    5. "pressure_level": "low", "medium", or "high" given the match context.
    6. "tactical_insight": Tactical insight about this delivery and shot.
    7. "match_context": Context-aware match narrative.
    8. "next_ball_prediction": Predict the next ball delivery the bowler should bowl.

    Respond ONLY with valid JSON. No markdown.
    """

    genai.configure(api_key=api_key)

    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image_data])
            text = response.text.replace('```json', '').replace('```', '').strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"error": "Failed to parse Gemini response", "raw": text}
        except Exception as e:
            last_error = str(e)
            logging.warning(f"Model {model_name} failed: {last_error[:80]}")
            continue

    # All models failed — fall back to simulation
    logging.warning(f"All Gemini models failed. Last error: {last_error}")
    result = _smart_simulate(event, context)
    if last_error:
        if "quota" in last_error.lower() or "rate" in last_error.lower():
            result["api_note"] = "Simulation mode (API quota exhausted). Get a free key at aistudio.google.com"
        elif "invalid" in last_error.lower() or "key" in last_error.lower():
            result["api_note"] = "Simulation mode (Invalid API key). Get a free key at aistudio.google.com"
        else:
            result["api_note"] = f"Simulation mode ({last_error[:60]})"
    return result
