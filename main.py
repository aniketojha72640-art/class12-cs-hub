import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Class 12 CS Python Hub")

# Catalog of your management projects (scalable to 40+ projects)
PROJECTS = [
    {
        "id": "1",
        "title": "STUDENT RECORD SYSTEM",
        "category": "ACADEMIC MANAGEMENT",
        "description": "Complete Class 12 CS project featuring MySQL database connectivity, CRUD operations, and automated report card generation.",
        "zip_file": "demo_project.zip",
        "color": "#38bdf8"
    },
    {
        "id": "2",
        "title": "HOSPITAL MANAGEMENT",
        "category": "HEALTHCARE SYSTEM",
        "description": "Full patient admissions tracker, doctor appointment scheduler, and automated billing engine in pure Python.",
        "zip_file": "demo_project.zip",
        "color": "#34d399"
    },
    {
        "id": "3",
        "title": "LIBRARY CATALOG SYSTEM",
        "category": "RESOURCE TRACKER",
        "description": "Automated book check-in/check-out system with late fine calculator, ISBN lookup, and full SQL transaction handling.",
        "zip_file": "demo_project.zip",
        "color": "#a78bfa"
    },
    {
        "id": "4",
        "title": "BANKING TRANSACTION SYSTEM",
        "category": "FINANCE & LOGS",
        "description": "High-accuracy transaction engine with PIN verification, account balance tracking, and PDF passbook generation.",
        "zip_file": "demo_project.zip",
        "color": "#f59e0b"
    }
]

@app.get("/api/projects")
def get_projects():
    return PROJECTS

@app.get("/api/download/{project_id}")
def download_project(project_id: str):
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    file_path = os.path.join("projects", project["zip_file"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="ZIP file not found")
        
    return FileResponse(
        path=file_path,
        filename=f"{project['title'].lower().replace(' ', '_')}.zip",
        media_type="application/zip"
    )

# Mount front-end static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
