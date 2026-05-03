from fastapi import FastAPI, File, UploadFile, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import base64
from dotenv import load_dotenv

from agents.vision_agent import process_image
from agents.structuring_agent import extract_event
from agents.context_agent import get_live_context
from agents.intelligence_agent import generate_insights
from agents.stats_agent import stats_tracker
from agents.explanation_agent import explain_insight

load_dotenv()

app = FastAPI(title="Cricket Vision Intelligence")

# Ensure directories exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_location = f"static/uploads/{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        # 1. Vision Agent
        vision_result = process_image(file_location)
        
        # 2. Structuring Agent
        event_data = extract_event(vision_result)
        
        # 3. Context Agent (Fetch Live Match Data)
        context_data = get_live_context()
        
        # 4. Intelligence Agent (Gemini)
        # Pass the original image to Gemini for real multimodal analysis!
        insights = generate_insights(file_location, event_data, context_data)
        
        # 5. Stats Agent
        stats_tracker.update_stats(insights)
        
        return JSONResponse(content={
            "status": "success",
            "vision": vision_result,
            "event": event_data,
            "context": context_data,
            "insights": insights,
            "stats": stats_tracker.get_stats()
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/explain")
async def explain_data(request: Request):
    data = await request.json()
    insight_text = data.get("insight")
    if not insight_text:
        raise HTTPException(status_code=400, detail="No insight provided")
    
    explanation = explain_insight(insight_text)
    return JSONResponse(content={"explanation": explanation})

@app.get("/api/stats")
async def get_stats():
    return JSONResponse(content=stats_tracker.get_stats())
