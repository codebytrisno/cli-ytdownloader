#!/usr/bin/env python3
import os
import sys
import shutil
import webbrowser

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp not installed. Run: pip install yt-dlp")
    sys.exit(1)

# Try to find ffmpeg in common Windows locations
def find_ffmpeg():
    ffmpeg_names = ['ffmpeg', 'ffmpeg.exe']
    common_paths = [
        os.path.join(os.environ.get('ProgramFiles', ''), 'ffmpeg', 'bin'),
        os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'ffmpeg', 'bin'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages', 'FFmpeg', 'ffmpeg', 'bin'),
    ]
    
    # Check PATH first
    if shutil.which('ffmpeg'):
        return shutil.which('ffmpeg')
    
    # Check common install locations
    for path in common_paths:
        for name in ffmpeg_names:
            full_path = os.path.join(path, name)
            if os.path.exists(full_path):
                return full_path
    return None


def check_ffmpeg():
    """Check if FFmpeg is installed and available in PATH."""
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path is None:
        print("WARNING: FFmpeg tidak ditemukan di sistem.")
        print("Silakan install FFmpeg untuk konversi MP3:")
        print("  - Windows: winget install ffmpeg")
        print("  - atau download dari https://ffmpeg.org/download.html")
        return None
    return ffmpeg_path


def show_menu():
    print("\n" + "=" * 50)
    print("  CLI YouTube Downloader (cli-ytdownloader)")
    print("=" * 50)
    print("1. Single Download")
    print("2. File List Download")
    print("3. Donasi")
    print("4. Keluar")
    print("=" * 50)


def donasi():
    """Open donation page in browser."""
    print("\nTerima kasih untuk donasi! Membuka halaman donasi...")
    webbrowser.open("https://sociabuzz.com/trisnosanjaya")
    print("Jika browser tidak terbuka otomatis, kunjungi:")
    print("https://sociabuzz.com/trisnosanjaya")


def download_audio(url, output_dir="downloads", ffmpeg_path=None, download_format='mp3'):
    os.makedirs(output_dir, exist_ok=True)
    
    # Set format based on user choice
    if download_format == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': True,
        }
        
        # Only add postprocessor if ffmpeg is available
        if ffmpeg_path:
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            
            # Check if ffprobe exists in the same directory
            ffprobe_exe = os.path.join(ffmpeg_dir, 'ffprobe.exe')
            ffprobe_exists = os.path.exists(ffprobe_exe) or shutil.which('ffprobe') or shutil.which('ffprobe.exe')
            
            if ffprobe_exists:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
                ydl_opts['ffmpeg_location'] = ffmpeg_dir
                print("  (FFmpeg terdeteksi - akan dikonversi ke MP3 192kbps)")
            else:
                print("  Peringatan: ffprobe tidak ditemukan")
                print("  (akan disimpan format audio asli)")
        else:
            print("  (Tidak ada FFmpeg - akan menyimpan format audio asli)")
    else:  # mp4 format
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': True,
        }
        print("  (Mendownload video MP4)")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        error_msg = str(e)
        if 'ffmpeg' in error_msg.lower() or 'ffprobe' in error_msg.lower():
            print(f"Error: FFmpeg/ffprobe tidak ditemukan. Install FFmpeg untuk konversi MP3.")
        else:
            print(f"Error downloading {url}: {e}")
        return False


def single_download(ffmpeg_path=None, download_format='mp3'):
    url = input("\nMasukkan URL YouTube: ").strip()
    if not url:
        print("URL tidak boleh kosong!")
        return
    
    print(f"\nMendownload: {url}")
    if download_audio(url, ffmpeg_path=ffmpeg_path, download_format=download_format):
        print("Download selesai!")


def batch_download(ffmpeg_path=None, download_format='mp3'):
    file_path = input("\nMasukkan path file .txt: ").strip()
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' tidak ditemukan!")
        return
    
    urls = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    
    if not urls:
        print("Tidak ada URL yang valid dalam file!")
        return
    
    total = len(urls)
    success_count = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\nProgress: {i}/{total}")
        if download_audio(url, ffmpeg_path=ffmpeg_path, download_format=download_format):
            success_count += 1
    
    print(f"\nBatch selesai! {success_count}/{total} berhasil didownload.")


def main():
    # Check ffmpeg on startup
    ffmpeg_path = check_ffmpeg()
    if ffmpeg_path is None:
        print("\nTekan Enter untuk melanjutkan (akan menyimpan format audio asli tanpa MP3)...")
        input()
    else:
        print(f"\nFFmpeg ditemukan: {ffmpeg_path}")
    
    # Ask for download format at the start
    print("\nPilih format download:")
    print("1. MP3 (Audio only)")
    print("2. MP4 (Video)")
    format_choice = input("Pilih format (1-2, default 1): ").strip()
    download_format = 'mp3' if format_choice != '2' else 'mp4'
    
    while True:
        show_menu()
        choice = input("Pilih menu (1-4): ").strip()
        
        if choice == '1':
            single_download(ffmpeg_path, download_format)
        elif choice == '2':
            batch_download(ffmpeg_path, download_format)
        elif choice == '3':
            donasi()
        elif choice == '4':
            print("\nKeluar program. Terima kasih!")
            break
        else:
            print("Pilihan tidak valid! Silakan pilih 1-4.")


if __name__ == "__main__":
    main()