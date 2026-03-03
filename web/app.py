"""Alldebrid-DL Web UI — FastAPI application."""

import asyncio
import json
import os

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import alldebrid
from downloader import download_manager, DownloadState

app = FastAPI(title="Alldebrid-DL")

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", os.path.expanduser("~/Downloads"))

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_api_key(request: Request) -> str | None:
    return request.session.get("api_key")


def require_auth(request: Request) -> str:
    key = get_api_key(request)
    if not key:
        raise _redirect_login()
    return key


def _redirect_login():
    from fastapi import HTTPException
    raise HTTPException(status_code=307, headers={"Location": "/login"})


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if get_api_key(request):
        return RedirectResponse("/magnets", status_code=302)
    return RedirectResponse("/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, api_key: str = Form(...)):
    if await alldebrid.verify_api_key(api_key):
        request.session["api_key"] = api_key
        return RedirectResponse("/magnets", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Clé API invalide"})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


@app.get("/magnets", response_class=HTMLResponse)
async def magnets_list(request: Request):
    key = get_api_key(request)
    if not key:
        return RedirectResponse("/login", status_code=302)
    try:
        magnets = await alldebrid.get_magnets(key)
    except Exception as e:
        magnets = []
        return templates.TemplateResponse("magnets.html", {
            "request": request, "magnets": magnets, "error": str(e),
            "downloads": download_manager.get_all_jobs(),
        })
    return templates.TemplateResponse("magnets.html", {
        "request": request, "magnets": magnets, "error": None,
        "downloads": download_manager.get_all_jobs(),
    })


@app.get("/magnets/{magnet_id}", response_class=HTMLResponse)
async def magnet_detail(request: Request, magnet_id: int):
    key = get_api_key(request)
    if not key:
        return RedirectResponse("/login", status_code=302)
    try:
        magnet = await alldebrid.get_magnet(key, magnet_id)
        files = alldebrid.extract_files(magnet.get("files", []))
    except Exception as e:
        return templates.TemplateResponse("magnet_detail.html", {
            "request": request, "magnet": None, "files": [], "error": str(e),
            "job": None,
        })
    job = download_manager.get_job(magnet_id)
    return templates.TemplateResponse("magnet_detail.html", {
        "request": request, "magnet": magnet, "files": files, "error": None,
        "job": job.to_dict() if job else None,
    })


@app.post("/magnets/upload")
async def upload_torrent(request: Request, file: UploadFile = File(...)):
    key = get_api_key(request)
    if not key:
        return RedirectResponse("/login", status_code=302)
    content = await file.read()
    try:
        await alldebrid.upload_torrent(key, content, file.filename)
    except Exception as e:
        return templates.TemplateResponse("magnets.html", {
            "request": request, "magnets": [], "error": f"Erreur upload: {e}",
            "downloads": download_manager.get_all_jobs(),
        })
    return RedirectResponse("/magnets", status_code=302)


@app.post("/magnets/{magnet_id}/download")
async def start_download(request: Request, magnet_id: int):
    key = get_api_key(request)
    if not key:
        return RedirectResponse("/login", status_code=302)
    download_manager.start_download(key, magnet_id, DOWNLOAD_DIR)
    return RedirectResponse(f"/magnets/{magnet_id}", status_code=302)


@app.post("/magnets/{magnet_id}/stop")
async def stop_download(request: Request, magnet_id: int):
    key = get_api_key(request)
    if not key:
        return RedirectResponse("/login", status_code=302)
    download_manager.stop_download(magnet_id)
    return RedirectResponse(f"/magnets/{magnet_id}", status_code=302)


@app.get("/api/downloads/{magnet_id}/progress")
async def download_progress_sse(request: Request, magnet_id: int):
    async def event_stream():
        while True:
            job = download_manager.get_job(magnet_id)
            if job is None:
                yield f"data: {json.dumps({'state': 'not_found'})}\n\n"
                break
            yield f"data: {json.dumps(job.to_dict())}\n\n"
            if job.state in (DownloadState.COMPLETED, DownloadState.ERROR):
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/downloads")
async def all_downloads():
    return download_manager.get_all_jobs()
