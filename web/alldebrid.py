"""Alldebrid API async client."""

import httpx
from urllib.parse import quote

BASE_URL = "https://api.alldebrid.com/v4.1"
AGENT = "alldebrid-dl"


async def _get(path: str, api_key: str, params: dict | None = None) -> dict:
    params = params or {}
    params.update({"agent": AGENT, "apikey": api_key})
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{BASE_URL}{path}", params=params)
        r.raise_for_status()
        return r.json()


async def verify_api_key(api_key: str) -> bool:
    try:
        data = await _get("/user", api_key)
        return "error" not in data
    except Exception:
        return False


async def get_magnets(api_key: str) -> list[dict]:
    data = await _get("/magnet/status", api_key)
    if "error" in data:
        raise Exception(data["error"].get("message", "Unknown error"))
    magnets = data.get("data", {}).get("magnets", [])
    if isinstance(magnets, dict):
        magnets = [magnets]
    return magnets


async def get_magnet(api_key: str, magnet_id: int) -> dict:
    data = await _get("/magnet/status", api_key, {"id": str(magnet_id)})
    if "error" in data:
        raise Exception(data["error"].get("message", "Unknown error"))
    return data.get("data", {}).get("magnets", {})


def _walk_files(file_tree: list[dict], prefix: str = "") -> list[dict]:
    """Recursively extract files from nested Alldebrid file structure."""
    results = []
    for item in file_tree:
        name = item.get("n", "")
        link = item.get("l")
        children = item.get("e")
        path = f"{prefix}/{name}" if prefix else name
        if link:
            results.append({"path": path, "link": link, "size": item.get("s", 0)})
        elif children:
            results.extend(_walk_files(children, path))
    return results


def extract_files(file_tree: list[dict]) -> list[dict]:
    """Extract files, skipping the root folder to avoid duplicate directory."""
    # If single root folder, descend into it directly
    if len(file_tree) == 1 and "e" in file_tree[0] and not file_tree[0].get("l"):
        return _walk_files(file_tree[0]["e"])
    return _walk_files(file_tree)


async def unlock_link(api_key: str, link: str) -> str:
    data = await _get("/link/unlock", api_key, {"link": link})
    if "error" in data:
        raise Exception(data["error"].get("message", "Unknown error"))
    return data["data"]["link"]


async def upload_torrent(api_key: str, file_content: bytes, filename: str) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            f"{BASE_URL}/magnet/upload/file",
            params={"agent": AGENT, "apikey": api_key},
            files={"files[]": (filename, file_content)},
        )
        r.raise_for_status()
        data = r.json()
    if "error" in data:
        raise Exception(data["error"].get("message", "Unknown error"))
    return data.get("data", {})
