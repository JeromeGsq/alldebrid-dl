# alldebrid-dl

A single bash script to download all files from an [Alldebrid](https://alldebrid.com) magnet — with full directory structure preserved.

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
[2/258] DCIM/Camera/2025-02-28 14.43.15.jpg
  OK
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All files downloaded successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Features

- **Preserves directory structure** — files land exactly where they should
- **Resumes interrupted downloads** — uses `wget --continue`
- **Auto-configuration** — prompts for your API key on first run and saves it
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

## Configuration

On first run, the script will prompt you for your API key and save it to `~/.config/alldebrid-dl/config`.

You can also set it manually:

```bash
mkdir -p ~/.config/alldebrid-dl
echo 'ALLDEBRID_API_KEY="your_key"' > ~/.config/alldebrid-dl/config
chmod 600 ~/.config/alldebrid-dl/config
```

Alternatively, the script also reads from a `.env` file in the current directory or an `ALLDEBRID_API_KEY` environment variable.

## Usage

```bash
alldebrid-dl <magnet_id> [output_dir]
```

- `magnet_id` — the number shown in your Alldebrid magnet list URL or dashboard
- `output_dir` — optional parent directory (defaults to `~/Downloads`)

Files are downloaded to `<output_dir>/<magnet_name>/`.

## How it works

1. Fetches the magnet's file tree from the Alldebrid API (v4.1)
2. Recursively walks the nested JSON structure to extract every file path + link
3. Unlocks each link through Alldebrid's CDN
4. Downloads with `wget`, preserving the original directory tree

## License

[MIT](LICENSE)
