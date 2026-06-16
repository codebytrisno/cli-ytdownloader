# CLI YouTube Downloader

A simple command-line tool to download YouTube videos as MP3 or MP4 format.

## Features

- **Single Download**: Download one YouTube video/audio
- **Batch Download**: Download multiple videos from a text file
- **MP3/MP4 Selection**: Choose audio-only (MP3) or video (MP4) format
- **Automatic Conversion**: Convert to MP3 192kbps (requires FFmpeg)
- **Progress Indicator**: Shows progress for batch downloads
- **Donation Support**: Support the developer via Sociabuzz

## Demo

```
==================================================
  CLI YouTube Downloader (cli-ytdownloader)
==================================================
1. Single Download
2. File List Download
3. Donasi
4. Keluar
==================================================
Pilih menu (1-4): 1

Masukkan URL YouTube: https://youtube.com/watch?v=...
Mendownload: https://youtube.com/watch?v=...
  (FFmpeg terdeteksi - akan dikonversi ke MP3 192kbps)
[download] 100% of 5.23MiB in 00:00:02
Download selesai!
```

## Requirements

- Python 3.x
- yt-dlp: `pip install yt-dlp`
- FFmpeg (required for MP3 conversion)

## Installing FFmpeg on Windows

### Option 1: Using winget (recommended)
```cmd
winget install ffmpeg
```

### Option 2: Using chocolatey
```cmd
choco install ffmpeg
```

### Option 3: Manual installation
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to system PATH

## Installation

```cmd
pip install -r requirements.txt
```

## Usage

```cmd
python cli-ytdownloader.py
```

### Batch Download Format

Create a text file (e.g., `list.txt`) with one YouTube URL per line:

```
# Komentar akan diabaikan
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/QkPk1mXIMZo
```

## Project Structure

```
cli-ytdownloader/
├── cli-ytdownloader.py  # Main program
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── list.txt           # Example batch file
```

## License

MIT License - Feel free to use and modify!

## Support

If you find this tool helpful, consider supporting the developer:
- [Donate via Sociabuzz](https://sociabuzz.com/trisnosanjaya)