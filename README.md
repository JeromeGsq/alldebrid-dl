# alldebrid-dl

A single bash script to download all files from an [Alldebrid](https://alldebrid.com) magnet — with full directory structure preserved.

```
$ ./alldebrid-dl 470037424

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Alldebrid Downloader — Magnet #470037424
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fetching magnet status...
Magnet ready: Minishoot.Adventures
258 file(s) found
Destination: ~/Downloads/alldebrid_470037424

[1/258] /Windows/Minishoot.exe
  OK
[2/258] /Windows/Minishoot_Data/app.info
  OK
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All files downloaded successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Features

- **Preserves directory structure** — files land exactly where they should
- **Resumes interrupted downloads** — uses `wget --continue`
- **Single file, zero config** — one script, no frameworks, no bloat
- **Progress tracking** — real-time progress bar per file

## Requirements

- `curl`, `jq`, `wget`, `python3` (all available via `brew install` or your package manager)
- An [Alldebrid](https://alldebrid.com) account & API key ([get one here](https://alldebrid.com/apikeys))

## Installation

### Homebrew (macOS)

```bash
brew tap jeromegsq/alldebrid-dl
brew install alldebrid-dl
```

### Manual (macOS & Linux)

```bash
git clone https://github.com/jeromegsq/alldebrid-dl.git
cd alldebrid-dl
make install
```

### Configuration

```bash
cp .env.example .env
```

Edit `.env` with your API key:

```
ALLDEBRID_API_KEY="your_api_key_here"
```

> When installed via `make install` or `brew`, the script looks for `.env` in the current directory, so keep it wherever you run the command from.

## Usage

```bash
alldebrid-dl <magnet_id>
```

The magnet ID is the number shown in your Alldebrid magnet list URL or dashboard.

Files are downloaded to `~/Downloads/alldebrid_<magnet_id>/`.

## How it works

1. Fetches the magnet's file tree from the Alldebrid API (v4.1)
2. Recursively walks the nested JSON structure to extract every file path + link
3. Unlocks each link through Alldebrid's CDN
4. Downloads with `wget`, preserving the original directory tree

## License

[MIT](LICENSE)
