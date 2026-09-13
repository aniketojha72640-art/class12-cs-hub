import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List


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


# ==========================================
# SUPER ADMIN VAULT - ISOLATED FROM FRONTEND
# ==========================================
import os
from fastapi import Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import create_client, Client

# Load Keys from Render Environment
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "fallback_lock")

# Connect to Supabase
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_security_clearance(request: Request):
    if request.cookies.get("admin_lock") != "granted":
        raise HTTPException(status_code=401, detail="Access Denied.")

# Login Screen (with Session Storage Tag)
@app.get("/admin", response_class=HTMLResponse)
async def admin_portal(request: Request):
    if request.cookies.get("admin_lock") == "granted":
        try:
            with open("templates/admin.html", "r") as file:
                return file.read()
        except FileNotFoundError:
            return "Error: Make sure admin.html is inside a 'templates' folder!"

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Login</title>
    </head>
    <body style="background:#111; color:white; font-family:system-ui; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <form onsubmit="sessionStorage.setItem('vault_auth', 'true');" action="/admin/login" method="POST" style="background:#222; padding:30px; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,0.5); text-align:center; width:90%; max-width:400px;">
            <h2 style="margin-top:0; color:#f39c12;">Admin Vault</h2>
            <input type="password" id="pwd" name="password" placeholder="Master Password" style="width:100%; padding:12px; margin-bottom:10px; border-radius:6px; border:none; background:#333; color:white;" required>
            <div style="text-align: left; margin-bottom: 20px; font-size: 14px; color: #aaa;">
                <input type="checkbox" id="showPwd" onclick="document.getElementById('pwd').type = this.checked ? 'text' : 'password'">
                <label for="showPwd" style="cursor:pointer;">Show Password</label>
            </div>
            <button type="submit" style="width:100%; padding:12px; background:#f39c12; border:none; border-radius:6px; font-weight:bold; cursor:pointer; color:#111; margin-bottom: 15px;">Authenticate</button>
            <a href="/" style="display:block; color:#aaa; text-decoration:none; font-size:14px; padding:10px; border:1px solid #444; border-radius:6px;">← Back to Main Website</a>
        </form>
    </body>
    </html>
    """

@app.post("/admin/login")
async def process_login(password: str = Form(...)):
    if password == ADMIN_PASS:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="admin_lock", value="granted", httponly=True, secure=True)
        return response
    return HTMLResponse("<h1 style='color:red; text-align:center; margin-top:50px;'>INCORRECT PASSWORD</h1>", status_code=401)

@app.post("/admin/logout")
async def logout():
    response = RedirectResponse(url="/admin", status_code=303)
    response.delete_cookie("admin_lock")
    return response

# Cloud Data APIs
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
    zipfile: UploadFile = File(None),
    images: List[UploadFile] = File(None)
):
    zip_name = ""
    img_names = []
    if zipfile and zipfile.filename:
        zip_name = zipfile.filename
        supabase.storage.from_("projects-vault").upload(path=f"files/{zip_name}", file=await zipfile.read())
    if images:
        for img in images:
            if img.filename:
                supabase.storage.from_("images-vault").upload(path=f"covers/{img.filename}", file=await img.read())
                img_names.append(img.filename)
    supabase.table("projects").insert({
        "title": title, "description": desc, "filename": zip_name, "image_filename": ",".join(img_names)
    }).execute()
    return {"status": "Uploaded"}

@app.put("/api/admin/projects", dependencies=[Depends(verify_security_clearance)])
async def update_cloud_project(
    id: int = Form(...),
    title: str = Form(...),
    desc: str = Form(...),
    zipfile: UploadFile = File(None),
    images: List[UploadFile] = File(None)
):
    update_data = {"title": title, "description": desc}
    if zipfile and zipfile.filename:
        old = supabase.table("projects").select("filename").eq("id", id).execute()
        if old.data and old.data[0].get("filename"):
            supabase.storage.from_("projects-vault").remove([f"files/{old.data[0]['filename']}"])
        supabase.storage.from_("projects-vault").upload(path=f"files/{zipfile.filename}", file=await zipfile.read())
        update_data["filename"] = zipfile.filename
        
    if images and images[0].filename:
        old = supabase.table("projects").select("image_filename").eq("id", id).execute()
        if old.data and old.data[0].get("image_filename"):
            for old_img in old.data[0]['image_filename'].split(","):
                supabase.storage.from_("images-vault").remove([f"covers/{old_img}"])
        new_imgs = []
        for img in images:
            if img.filename:
                supabase.storage.from_("images-vault").upload(path=f"covers/{img.filename}", file=await img.read())
                new_imgs.append(img.filename)
        update_data["image_filename"] = ",".join(new_imgs)
        
    supabase.table("projects").update(update_data).eq("id", id).execute()
    return {"status": "Updated"}

@app.delete("/api/admin/projects", dependencies=[Depends(verify_security_clearance)])
async def remove_from_cloud(request: Request):
    data = await request.json()
    for pid in data.get("ids", []):
        proj_data = supabase.table("projects").select("filename, image_filename").eq("id", pid).execute()
        if proj_data.data:
            proj = proj_data.data[0]
            if proj.get("filename"):
                supabase.storage.from_("projects-vault").remove([f"files/{proj.get('filename')}"])
            if proj.get("image_filename"):
                for img in proj.get("image_filename").split(","):
                    supabase.storage.from_("images-vault").remove([f"covers/{img}"])
        supabase.table("projects").delete().eq("id", pid).execute()
    return {"status": "Deleted"}


# Mount front-end static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
