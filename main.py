from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

import memory
from fastapi import FastAPI
import ollama
from scraper import search_company, scrape_website
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


from agents.orchestrator import run_agents
from fastapi.responses import JSONResponse
import traceback


@app.get("/analyze")
def analyze(company: str):
    try:
        return run_agents(company)
    except Exception as e:
        logger.exception("Unhandled exception in /analyze")
        return JSONResponse(status_code=500, content={
            "error": "Error analyzing company. See server logs for details.",
            "detail": str(e)
        })
    

@app.get("/history")
def get_history():
    return {
        "companies": memory.get_all_companies()
    }