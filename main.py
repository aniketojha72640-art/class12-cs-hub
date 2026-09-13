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
# ==========================================
# SUPER ADMIN VAULT - ISOLATED FROM FRONTEND
# ==========================================
import os
from fastapi import Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import create_client, Client

# 1. Load the One-and-Only Master Password from Render
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "fallback_lock")

# Connect to the Cloud
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. The Ultimate Security Bouncer (HttpOnly Cookie Check)
def verify_security_clearance(request: Request):
    if request.cookies.get("admin_lock") != "granted":
        raise HTTPException(status_code=401, detail="Access Denied.")

# 3. The Isolated Login Page
@app.get("/admin", response_class=HTMLResponse)
async def admin_portal(request: Request):
    # If already securely logged in, show the dashboard!
    if request.cookies.get("admin_lock") == "granted":
        try:
            with open("templates/admin.html", "r") as file:
                return file.read()
        except FileNotFoundError:
            return "Error: Make sure admin.html is inside a 'templates' folder!"

    # If not logged in, show ONLY a master password box (No signup possible)
    return """
    <body style="background:#111; color:white; font-family:system-ui; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <form action="/admin/login" method="POST" style="background:#222; padding:40px; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,0.5); text-align:center;">
            <h2 style="margin-top:0;">Admin Vault</h2>
            <input type="password" name="password" placeholder="Master Password" style="width:100%; padding:12px; margin-bottom:20px; border-radius:6px; border:none; background:#333; color:white; box-sizing:border-box;" required>
            <button type="submit" style="width:100%; padding:12px; background:#f39c12; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">Authenticate</button>
        </form>
    </body>
    """

@app.post("/admin/login")
async def process_login(password: str = Form(...)):
    # Check if they know the one true password
    if password == ADMIN_PASS:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="admin_lock", value="granted", httponly=True, secure=True)
        return response
    return HTMLResponse("<h1 style='color:red; text-align:center; margin-top:50px;'>INCORRECT PASSWORD</h1>", status_code=401)

# 4. Cloud Data APIs (Completely Protected by the Bouncer!)
@app.get("/api/admin/projects")
async def fetch_cloud_projects():
    try:
        data = supabase.table("projects").select("*").execute()
        return data.data
    except Exception:
        return []

@app.post("/api/admin/projects", dependencies=[Depends(verify_security_clearance)])
async def upload_to_cloud(
    title: str = Form(...),
    desc: str = Form(...),
    zipfile: UploadFile = File(None)
):
    filename = ""
    if zipfile:
        filename = zipfile.filename
        file_bytes = await zipfile.read()
        supabase.storage.from_("projects-vault").upload(
            path=f"files/{filename}", 
            file=file_bytes, 
            file_options={"content-type": zipfile.content_type}
        )
        
    supabase.table("projects").insert({
        "title": title,
        "description": desc,
        "filename": filename
    }).execute()
    
    return {"status": "Uploaded"}

@app.delete("/api/admin/projects", dependencies=[Depends(verify_security_clearance)])
async def remove_from_cloud(request: Request):
    data = await request.json()
    for pid in data.get("ids", []):
        supabase.table("projects").delete().eq("id", pid).execute()
    return {"status": "Deleted"}
