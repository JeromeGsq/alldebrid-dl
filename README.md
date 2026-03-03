# alldebrid-dl

Download files from [Alldebrid](https://alldebrid.com) magnets — available as a **CLI script** and a **self-hosted web UI**.

## CLI

A single bash script that downloads all files from an Alldebrid magnet with full directory structure preserved.

```
$ alldebrid-dl 470037424

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Alldebrid Downloader — Magnet #470037424
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fetching magnet status...
Magnet ready: Family-Pictures
258 file(s) found
Destination: ~/Downloads/Family-Pictures

[1/258] DCIM/Camera/2025-02-28 14.43.14.jpg
  OK
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All files downloaded successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### CLI Features

- **Preserves directory structure** — files land exactly where they should
- **Resumes interrupted downloads** — uses `wget --continue`
- **Auto-configuration** — prompts for your API key on first run and saves it
- **Single file, zero config** — one script, no frameworks, no bloat
- **Progress tracking** — real-time progress bar per file

### CLI Requirements

- `curl`, `jq`, `wget`, `python3` (all available via `brew install` or your package manager)
- An [Alldebrid](https://alldebrid.com) account & API key ([get one here](https://alldebrid.com/apikeys))

### CLI Installation

#### Homebrew (macOS)

```bash
brew tap jeromegsq/alldebrid-dl
brew install alldebrid-dl
```

#### Manual (macOS & Linux)

```bash
git clone https://github.com/jeromegsq/alldebrid-dl.git
cd alldebrid-dl
make install
```

### CLI Usage

```bash
alldebrid-dl <magnet_id> [output_dir]
```

- `magnet_id` — the number shown in your Alldebrid magnet list URL or dashboard
- `output_dir` — optional parent directory (defaults to `~/Downloads`)

### CLI Configuration

On first run, the script will prompt you for your API key and save it to `~/.config/alldebrid-dl/config`.

You can also set it manually:

```bash
mkdir -p ~/.config/alldebrid-dl
echo 'ALLDEBRID_API_KEY="your_key"' > ~/.config/alldebrid-dl/config
chmod 600 ~/.config/alldebrid-dl/config
```

Alternatively, the script also reads from a `.env` file in the current directory or an `ALLDEBRID_API_KEY` environment variable.

---

## Web UI

A self-hosted web interface (Python/FastAPI) to manage your Alldebrid magnets from a browser. Designed to run as a container on a server and download files directly to a NAS.

### Web Features

- **Authentication via API key** — enter your Alldebrid API key to log in
- **List all magnets** — view status, size, and file count
- **Upload .torrent files** — add new magnets directly from the browser
- **Download to NAS** — one-click download of all files to a mounted directory
- **Real-time progress** — live progress tracking via Server-Sent Events (SSE)
- **Stop downloads** — cancel running downloads at any time
- **Dark theme** — clean, responsive interface

### Deployment with Podman / Docker

```bash
cd web
podman-compose up -d --build
```

Or manually:

```bash
podman build -t alldebrid-dl ./web
podman run -d --name alldebrid-dl-web \
  -p 8081:8081 \
  -v /mnt/nas/home/Downloads:/downloads \
  -e SECRET_KEY=your-secret-key \
  -e DOWNLOAD_DIR=/downloads \
  --restart unless-stopped \
  alldebrid-dl
```

Then open `http://your-server:8081` in your browser.

### Local Development

```bash
cd web
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DOWNLOAD_DIR=/path/to/downloads uvicorn app:app --port 8081
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-me-in-production` | Secret key for session cookie signing |
| `DOWNLOAD_DIR` | `~/Downloads` | Directory where files are downloaded |
| `PORT` | `8081` | Server port (set via uvicorn) |

### compose.yaml

The provided `web/compose.yaml` maps `/mnt/nas/home/Downloads` on the host to `/downloads` in the container. Adjust the volume path to match your NAS mount point.

---

## How it works

1. Fetches the magnet's file tree from the Alldebrid API (v4.1)
2. Recursively walks the nested JSON structure to extract every file path + link
3. Unlocks each link through Alldebrid's CDN
4. Downloads files while preserving the original directory tree

## License

[MIT](LICENSE)
