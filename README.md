# CLI YouTube Downloader

A command-line tool to download YouTube videos as MP3 or MP4 with a modern Rich-powered interactive UI.

## Features

- **Rich Interactive UI** — Styled panels, color-coded menus, progress bars, spinners
- **Single Download** — Download one YouTube video/audio
- **Batch Download** — Download multiple videos from a text file with progress bar & ETA
- **MP3/MP4 Selection** — Choose audio-only (MP3 192kbps) or video (MP4) format
- **Auto FFmpeg Install** — Download & install FFmpeg automatically from within the app
- **FFmpeg Detection** — Finds FFmpeg in PATH, common Windows locations, or local `ffmpeg/bin/`
- **Donation Support** — Support the developer via Sociabuzz

## Demo

```
┌─────────────────────────────────────────────┐
│           CLI YouTube Downloader            │
│             cli-ytdownloader                │
├─────────────────────────────────────────────┤
│              1.  Single Download            │
│              2.  File List Download         │
│              3.  Donasi                     │
│              4.  Keluar                     │
└─────────────────────────────────────────────┘
```

## Requirements

- Python 3.8+
- Dependencies installed via `pip install -r requirements.txt`

## Installation

```cmd
pip install -r requirements.txt
```

## Usage

```cmd
python cli-ytdownloader.py
```

On first run, if FFmpeg is not found, the program will offer to download it automatically.

### Batch Download Format

Create a text file (e.g., `list.txt`) with one YouTube URL per line:

```
# Komentar akan diabaikan
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/QkPk1mXIMZo
```

## How Auto FFmpeg Install Works

1. Program checks PATH, common install locations, and local `ffmpeg/bin/`
2. If not found, shows a prompt to auto-download (~60MB)
3. Downloads `ffmpeg-release-essentials.zip` from gyan.dev with progress bar
4. Extracts `ffmpeg.exe` and `ffprobe.exe` to `ffmpeg/bin/` (portable, no admin needed)
5. Ready to use — persists across sessions

## Project Structure

```
cli-ytdownloader/
├── cli-ytdownloader.py  # Main program
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── list.txt           # Example batch file
├── downloads/          # Downloaded videos/audio
└── ffmpeg/             # Auto-installed FFmpeg (gitignored)
    └── bin/
        ├── ffmpeg.exe
        └── ffprobe.exe
```

## License

MIT License - Feel free to use and modify!

## Support

If you find this tool helpful, consider supporting the developer:
- [Donate via Sociabuzz](https://sociabuzz.com/trisnosanjaya)
