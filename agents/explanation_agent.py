import google.generativeai as genai
import os

def explain_insight(insight_text: str) -> str:
    """
    Uses Gemini to explain the reasoning behind a given insight or classification.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        return "Explanation unavailable: Please configure your Gemini API Key in the .env file to enable AI explanations."
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are an expert cricket analyst. Explain the reasoning and cricket logic behind the following insight:
        "{insight_text}"
        
        Provide a concise, clear, and analytical explanation that a cricket fan or coach would appreciate. Use 2-3 sentences.
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating explanation: {str(e)}"
