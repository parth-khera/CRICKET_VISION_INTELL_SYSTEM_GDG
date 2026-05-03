import google.generativeai as genai
import os
import json
import logging

def generate_insights(image_path: str, event: dict, context: dict) -> dict:
    """
    Uses Gemini Pro API to visually analyze the uploaded photo, generate intelligence,
    and predict the next ball based on the event and live match context.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        # Return fallback if API key is not configured yet
        return {
            "shot_type": event.get('shot', 'Unknown').capitalize(),
            "intent": "Aggressive" if event.get('runs', 0) >= 4 else "Defensive",
            "pressure_level": "High" if context.get('match_phase') == 'death' else "Medium",
            "tactical_insight": "API Key missing. Showing simulated insight: The batter is looking to capitalize on width.",
            "match_context": f"Simulated: At {context.get('wickets')} wickets down in the {context.get('match_phase')} phase, preserving wickets is as crucial as scoring.",
            "next_ball_prediction": "Simulated Prediction: Bowler will likely bowl a slower ball outside off-stump to counter the aggression."
        }
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Read the image file to send to Gemini
        mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
        with open(image_path, "rb") as f:
            image_data = {"mime_type": mime_type, "data": f.read()}
        
        prompt = f"""
        You are an expert cricket analyst. I have provided an image of a cricket match.
        Please analyze the photo visually to understand what is happening.
        
        Also, factor in this real-time match context:
        {json.dumps(context, indent=2)}
        
        Based on the photo and the context, generate the following in strict JSON format:
        1. "shot_type": The type of shot played or action occurring in the photo.
        2. "intent": The intent of the batter (aggressive/defensive/rotational).
        3. "pressure_level": The pressure level (low/medium/high) considering the context.
        4. "tactical_insight": A short tactical insight about this specific delivery and shot seen in the photo.
        5. "match_context": A short, realistic match context insight combining the event and the phase of the game.
        6. "next_ball_prediction": Based on the batter's position in the photo and the current context, predict what the bowler should bowl next (Next Ball Prediction).
        
        Respond ONLY with valid JSON.
        """
        
        # Pass both the prompt and the image to the multimodal model
        response = model.generate_content([prompt, image_data])
        text = response.text.replace('```json', '').replace('```', '').strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse Gemini response as JSON", "raw": text}
            
    except Exception as e:
        error_msg = str(e)
        logging.warning(f"Gemini API Error: {error_msg}")
        
        # Graceful fallback so the demo keeps working even if the API key is rate-limited to 0.
        return {
            "shot_type": event.get('shot', 'Aggressive Shot').capitalize(),
            "intent": "Aggressive" if event.get('runs', 0) >= 4 else "Defensive",
            "pressure_level": "High" if context.get('match_phase') == 'death' else "Medium",
            "tactical_insight": f"Simulated Insight (API Rate Limited): The batter is using the crease well to counter the bowling plan.",
            "match_context": f"Simulated: At {context.get('wickets')} wickets down in the {context.get('match_phase')} phase, the current strategy is critical.",
            "next_ball_prediction": "Simulated Prediction: The bowler is likely to change pace and bowl a slower delivery outside the off stump.",
            "error_note": "Your Gemini API key has a quota limit of 0 in your region. Showing simulated data."
        }
