# CLI YouTube Downloader

A command-line tool to download YouTube videos as MP3 or MP4, plus a modern **GUI version** built with CustomTkinter.

## Features

- **Dual Interface** — CLI (Rich-powered) & GUI (CustomTkinter)
- **Single Download** — Download one YouTube video/audio
- **Batch Download** — Parallel download (3x) from a text file
- **Real-time Progress** — Live percentage, speed & ETA in both CLI & GUI
- **MP3 Quality Options** — 128kbps / 192kbps / 320kbps / VBR 0 (Best)
- **MP4 Quality Options** — 720p (HD) / 1080p (Full HD) / Best
- **Auto FFmpeg Install** — Download & install FFmpeg automatically
- **FFmpeg Detection** — Finds FFmpeg in PATH, common Windows locations, or local `ffmpeg/bin/`
- **YouTube 403 Bypass** — Uses Android + Web player clients to avoid throttling
- **Donation Support** — Support the developer via Sociabuzz

## Requirements

- Python 3.8+
- Dependencies: `pip install -r requirements.txt`

## Installation

```cmd
pip install -r requirements.txt
```

For GUI version on Linux:
```cmd
pip install customtkinter pillow
```

## Usage

### CLI Version
```cmd
python cli-ytdownloader.py
```

### GUI Version
```cmd
python ytdownloader-gui.py
```

On first run, if FFmpeg is not found, the program will offer to download it automatically.

### Batch Download Format

Create a text file (e.g., `list.txt`) with one YouTube URL per line:

```
# Comments are ignored
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/QkPk1mXIMZo
```

## Quality Options

| MP3 | Bitrate |
|-----|---------|
| 128kbps | Fast, small file |
| 192kbps | Recommended (default) |
| 320kbps | High quality |
| VBR 0 | Best quality (variable bitrate) |

| MP4 | Resolution |
|-----|------------|
| 720p | HD |
| 1080p | Full HD (default) |
| Best | Highest available |

## How Auto FFmpeg Install Works

1. Program checks PATH, common install locations, and local `ffmpeg/bin/`
2. If not found, shows a prompt to auto-download (~60MB)
3. Downloads `ffmpeg-release-essentials.zip` from gyan.dev with progress bar
4. Extracts `ffmpeg.exe` and `ffprobe.exe` to `ffmpeg/bin/` (portable, no admin needed)
5. Ready to use — persists across sessions

## Project Structure

```
cli-ytdownloader/
├── cli-ytdownloader.py   # CLI version (Rich-powered)
├── ytdownloader-gui.py   # GUI version (CustomTkinter)
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── list.txt              # Example batch file
├── downloads/            # Downloaded videos/audio
└── ffmpeg/               # Auto-installed FFmpeg (gitignored)
    └── bin/
        ├── ffmpeg.exe
        └── ffprobe.exe
```

## License

MIT License - Feel free to use and modify!

## Support

If you find this tool helpful, consider supporting the developer:
- [Donate via Sociabuzz](https://sociabuzz.com/trisnosanjaya)
