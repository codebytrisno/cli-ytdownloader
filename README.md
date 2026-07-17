# CLI YouTube Downloader

CLI dan GUI downloader YouTube dengan fitur download MP3 / MP4, batch download, dan auto-install FFmpeg.

## Fitur

- **Dua Antarmuka** — CLI (Rich) & GUI (CustomTkinter)
- **Download Tunggal** — Download satu video/audio
- **Batch Download** — Download paralel (3x) dari file teks
- **Progress Real-time** — Persentase, kecepatan & ETA langsung
- **Kualitas MP3** — 128kbps / 192kbps / 320kbps / VBR 0 (Terbaik)
- **Kualitas MP4** — 720p (HD) / 1080p (Full HD) / Best
- **Auto FFmpeg** — Download & install FFmpeg otomatis
- **Bypass 403 YouTube** — Pakai Android + Web player client biar gak kena throttle
- **Donasi** — Dukung developer via Sociabuzz

## Requirements

- Python 3.8+
- `pip install -r requirements.txt`

## Instalasi

### Windows

1. **Install Python**
   - Download Python 3.8+ dari [python.org](https://www.python.org/downloads/)
   - **Centang** "Add Python to PATH" saat instalasi
   - Verifikasi: buka `CMD` atau `PowerShell`, ketik:
     ```cmd
     python --version
     ```

2. **Clone atau Download Repo**
   ```cmd
   git clone https://github.com/codebytrisno/cli-ytdownloader.git
   cd cli-ytdownloader
   ```
   Atau download ZIP dan extract.

3. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Jalankan**
   ```cmd
   python cli-ytdownloader.py    # CLI version
   python ytdownloader-gui.py    # GUI version
   ```

5. **FFmpeg** — Jika belum terinstall, program akan otomatis mendownload FFmpeg saat pertama kali dijalankan. Atau bisa juga [download manual](https://ffmpeg.org/download.html) dan taruh di `ffmpeg/bin/`.

### Linux

```cmd
pip install -r requirements.txt
python cli-ytdownloader.py
python ytdownloader-gui.py
```

## Cara Pakai

### CLI Version
```cmd
python cli-ytdownloader.py
```

### GUI Version
```cmd
python ytdownloader-gui.py
```

### Format Batch Download

Buat file teks (contoh: `list.txt`) dengan satu URL YouTube per baris:

```
# Komentar diabaikan
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/QkPk1mXIMZo
```

## Pilihan Kualitas

| MP3 | Bitrate |
|-----|---------|
| 128kbps | Cepat, file kecil |
| 192kbps | Recomended (default) |
| 320kbps | Kualitas tinggi |
| VBR 0 | Kualitas terbaik (variable bitrate) |

| MP4 | Resolusi |
|-----|----------|
| 720p | HD |
| 1080p | Full HD (default) |
| Best | Tertinggi yang tersedia |

## Cara Kerja Auto FFmpeg

1. Program cek PATH, lokasi instalasi umum, dan folder lokal `ffmpeg/bin/`
2. Kalau gak ketemu, muncul prompt buat download otomatis (~60MB)
3. Download `ffmpeg-release-essentials.zip` dari gyan.dev dengan progress bar
4. Extract `ffmpeg.exe` dan `ffprobe.exe` ke `ffmpeg/bin/` (portable, gak perlu admin)
5. Langsung bisa dipakai — tersimpan permanen

## Struktur Project

```
cli-ytdownloader/
├── cli-ytdownloader.py   # CLI version (Rich)
├── ytdownloader-gui.py   # GUI version (CustomTkinter)
├── requirements.txt      # Dependencies Python
├── README.md             # File ini
├── list.txt              # Contoh file batch
├── downloads/            # Hasil download (gitignored)
└── ffmpeg/               # FFmpeg auto-install (gitignored)
    └── bin/
        ├── ffmpeg.exe
        └── ffprobe.exe
```

## Lisensi

MIT License — Silakan pakai dan modifikasi!

## Dukungan

Kalau tool ini bermanfaat, dukung developer:
- [Donate via Sociabuzz](https://sociabuzz.com/trisnosanjaya)
