"""Download manager for background file downloads to NAS."""

import asyncio
import os
import time
from dataclasses import dataclass, field
from enum import Enum

import httpx

from alldebrid import extract_files, get_magnet, unlock_link


class DownloadState(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class FileProgress:
    path: str
    size: int = 0
    downloaded: int = 0
    state: DownloadState = DownloadState.PENDING
    error: str = ""


@dataclass
class DownloadJob:
    magnet_id: int
    magnet_name: str = ""
    state: DownloadState = DownloadState.PENDING
    files: list[FileProgress] = field(default_factory=list)
    current_file: int = 0
    total_files: int = 0
    error: str = ""
    started_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "magnet_id": self.magnet_id,
            "magnet_name": self.magnet_name,
            "state": self.state.value,
            "current_file": self.current_file,
            "total_files": self.total_files,
            "files": [
                {
                    "path": f.path,
                    "size": f.size,
                    "downloaded": f.downloaded,
                    "state": f.state.value,
                    "error": f.error,
                }
                for f in self.files
            ],
            "error": self.error,
        }


class DownloadManager:
    def __init__(self):
        self.jobs: dict[int, DownloadJob] = {}
        self._tasks: dict[int, asyncio.Task] = {}

    def get_job(self, magnet_id: int) -> DownloadJob | None:
        return self.jobs.get(magnet_id)

    def get_all_jobs(self) -> list[dict]:
        return [job.to_dict() for job in self.jobs.values()]

    def start_download(self, api_key: str, magnet_id: int, dest_dir: str):
        if magnet_id in self.jobs and self.jobs[magnet_id].state == DownloadState.DOWNLOADING:
            return  # Already running
        job = DownloadJob(magnet_id=magnet_id)
        self.jobs[magnet_id] = job
        task = asyncio.create_task(self._download(api_key, magnet_id, dest_dir, job))
        self._tasks[magnet_id] = task

    def stop_download(self, magnet_id: int):
        task = self._tasks.get(magnet_id)
        if task and not task.done():
            task.cancel()
        job = self.jobs.get(magnet_id)
        if job and job.state == DownloadState.DOWNLOADING:
            job.state = DownloadState.CANCELLED
            for f in job.files:
                if f.state == DownloadState.DOWNLOADING:
                    f.state = DownloadState.CANCELLED

    async def _download(self, api_key: str, magnet_id: int, dest_dir: str, job: DownloadJob):
        try:
            magnet = await get_magnet(api_key, magnet_id)
            job.magnet_name = magnet.get("filename", "download")
            files = extract_files(magnet.get("files", []))
            job.total_files = len(files)
            job.files = [FileProgress(path=f["path"], size=f["size"]) for f in files]
            job.state = DownloadState.DOWNLOADING

            magnet_dir = os.path.join(dest_dir, job.magnet_name)

            for i, file_info in enumerate(files):
                if job.state == DownloadState.CANCELLED:
                    break
                job.current_file = i + 1
                fp = job.files[i]
                fp.state = DownloadState.DOWNLOADING

                try:
                    dl_url = await unlock_link(api_key, file_info["link"])
                    out_path = os.path.join(magnet_dir, file_info["path"])
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)

                    async with httpx.AsyncClient(timeout=None, follow_redirects=True) as client:
                        async with client.stream("GET", dl_url) as resp:
                            resp.raise_for_status()
                            total = int(resp.headers.get("content-length", 0))
                            if total:
                                fp.size = total
                            with open(out_path, "wb") as f:
                                async for chunk in resp.aiter_bytes(chunk_size=1024 * 256):
                                    f.write(chunk)
                                    fp.downloaded += len(chunk)

                    fp.state = DownloadState.COMPLETED
                except Exception as e:
                    fp.state = DownloadState.ERROR
                    fp.error = str(e)
                    import traceback
                    traceback.print_exc()

            has_errors = any(f.state == DownloadState.ERROR for f in job.files)
            job.state = DownloadState.ERROR if has_errors and all(
                f.state == DownloadState.ERROR for f in job.files
            ) else DownloadState.COMPLETED

        except Exception as e:
            job.state = DownloadState.ERROR
            job.error = str(e)


download_manager = DownloadManager()
