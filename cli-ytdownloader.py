#!/usr/bin/env python3
import os
import sys
import shutil
import webbrowser
import urllib.request
import zipfile
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import (
    Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn,
)
from rich.align import Align
from rich import print as rprint

try:
    import yt_dlp
except ImportError:
    rprint("[bold red]Error: yt-dlp tidak terinstall. Jalankan: pip install yt-dlp[/]")
    sys.exit(1)

console = Console()

MP3_QUALITIES = {
    '128': {'label': '128kbps (Cepat, ukuran kecil)', 'value': '128'},
    '192': {'label': '192kbps (Recommended)', 'value': '192'},
    '320': {'label': '320kbps (High Quality)', 'value': '320'},
    'vbr0': {'label': 'VBR 0 (Terbaik - variable bitrate)', 'value': 'vbr0'},
}

MP4_QUALITIES = {
    '720': {'label': '720p (HD - cepat, kecil)', 'value': '720'},
    '1080': {'label': '1080p (Full HD - recommended)', 'value': '1080'},
    'best': {'label': 'Best (kualitas tertinggi)', 'value': 'best'},
}

CONCURRENT_WORKERS = 3


def find_ffmpeg():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_names = ['ffmpeg', 'ffmpeg.exe']
    common_paths = [
        os.path.join(script_dir, 'ffmpeg', 'bin'),
        os.path.join(os.environ.get('ProgramFiles', ''), 'ffmpeg', 'bin'),
        os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'ffmpeg', 'bin'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages', 'FFmpeg', 'ffmpeg', 'bin'),
    ]

    if shutil.which('ffmpeg'):
        return shutil.which('ffmpeg')

    for path in common_paths:
        for name in ffmpeg_names:
            full_path = os.path.join(path, name)
            if os.path.exists(full_path):
                return full_path
    return None


def check_ffmpeg():
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path is None:
        console.print(Panel(
            "[yellow]FFmpeg tidak ditemukan di sistem.[/]\n\n"
            "Pilihan:\n"
            "  [cyan]1.[/] Download otomatis FFmpeg (direkomendasikan)\n"
            "  [cyan]2.[/] Lewati (tanpa FFmpeg, fitur terbatas)\n"
            "  [cyan]3.[/] Install manual: winget install ffmpeg",
            title="[yellow]Peringatan[/]",
            border_style="yellow",
        ))
        choice = Prompt.ask("Pilih", choices=["1", "2"], default="1")
        if choice == "1":
            return auto_install_ffmpeg()
        return None
    return ffmpeg_path


FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def auto_install_ffmpeg():
    install_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg")
    bin_dir = os.path.join(install_dir, "bin")

    if os.path.exists(os.path.join(bin_dir, "ffmpeg.exe")):
        console.print(f"[green]FFmpeg sudah terinstall di:[/] [cyan]{bin_dir}[/]")
        return os.path.join(bin_dir, "ffmpeg.exe")

    console.print(Panel(
        "[bold cyan]Mengunduh FFmpeg...[/]\n\n"
        f"URL: {FFMPEG_URL}\n"
        f"Tujuan: {bin_dir}",
        border_style="cyan",
    ))

    os.makedirs(bin_dir, exist_ok=True)

    try:
        req = urllib.request.Request(
            FFMPEG_URL,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        )

        with urllib.request.urlopen(req) as resp:
            total = int(resp.headers.get('Content-Length', 0))

            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                tmp_path = tmp.name
                progress = Progress(
                    TextColumn("[bold cyan]Mengunduh FFmpeg...[/]"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeRemainingColumn(),
                    console=console,
                )
                with progress:
                    task = progress.add_task("", total=total)
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        tmp.write(chunk)
                        progress.update(task, advance=len(chunk))

        console.print("[green]Ekstraksi FFmpeg...[/]")
        with zipfile.ZipFile(tmp_path, 'r') as zf:
            ffmpeg_members = [m for m in zf.namelist() if m.endswith('ffmpeg.exe')]
            ffprobe_members = [m for m in zf.namelist() if m.endswith('ffprobe.exe')]

            for member in ffmpeg_members:
                zf.extract(member, install_dir)
                src = os.path.join(install_dir, member)
                dst = os.path.join(bin_dir, 'ffmpeg.exe')
                shutil.move(src, dst)

            for member in ffprobe_members:
                zf.extract(member, install_dir)
                src = os.path.join(install_dir, member)
                dst = os.path.join(bin_dir, 'ffprobe.exe')
                shutil.move(src, dst)

        for item in os.listdir(install_dir):
            item_path = os.path.join(install_dir, item)
            if item != 'bin' and os.path.isdir(item_path):
                shutil.rmtree(item_path)

        os.unlink(tmp_path)

        ffmpeg_exe = os.path.join(bin_dir, 'ffmpeg.exe')
        if os.path.exists(ffmpeg_exe):
            console.print(f"[bold green]FFmpeg berhasil diinstall![/] [cyan]{ffmpeg_exe}[/]")
            return ffmpeg_exe
        else:
            console.print("[bold red]Gagal mengekstrak FFmpeg.[/]")
            return None

    except Exception as e:
        console.print(f"[bold red]Gagal mendownload FFmpeg:[/] {e}")
        console.print("[yellow]Silakan install manual: winget install ffmpeg[/]")
        return None


def show_menu(download_format, quality):
    fmt_text = "MP3" if download_format == 'mp3' else "MP4"
    q_text = quality if download_format == 'mp4' else MP3_QUALITIES.get(quality, {}).get('label', quality)

    table = Table.grid(padding=1)
    table.add_column(style="cyan", justify="right")
    table.add_column(style="white")
    table.add_row("1.", "Single Download")
    table.add_row("2.", "File List Download")
    table.add_row("3.", "Donasi")
    table.add_row("4.", "Keluar")

    panel = Panel(
        Align.center(table),
        title=f"[bold green]CLI YouTube Downloader[/]",
        subtitle=f"[dim]{fmt_text} | {q_text} | {CONCURRENT_WORKERS}x parallel[/]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def donasi():
    console.print(Panel(
        "[green]Terima kasih untuk donasi![/] Membuka halaman donasi...",
        border_style="green",
    ))
    webbrowser.open("https://sociabuzz.com/trisnosanjaya")
    console.print("[dim]Jika browser tidak terbuka otomatis, kunjungi:[/]")
    console.print("[cyan]https://sociabuzz.com/trisnosanjaya[/]")


def build_ydl_opts(output_dir, ffmpeg_path, download_format, quality):
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'throttled_rate': '100M',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }

    if download_format == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'
        if ffmpeg_path:
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            ffprobe = shutil.which('ffprobe') or shutil.which('ffprobe.exe') or os.path.exists(os.path.join(ffmpeg_dir, 'ffprobe.exe'))
            if ffprobe:
                pp = {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}
                if quality == 'vbr0':
                    pp['preferredquality'] = '320'
                    ydl_opts['postprocessor_args'] = {'ffmpeg': ['-q:a', '0']}
                else:
                    pp['preferredquality'] = quality
                ydl_opts['postprocessors'] = [pp]
            ydl_opts['ffmpeg_location'] = ffmpeg_dir
    else:
        if ffmpeg_path:
            height_fmt = {
                '720': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]',
                '1080': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]',
                'best': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            }
            ydl_opts['format'] = height_fmt.get(quality, height_fmt['1080'])
            ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_path)
        else:
            fallback = {
                '720': 'best[height<=720][ext=mp4]/best[height<=720]',
                '1080': 'best[height<=1080][ext=mp4]/best[height<=1080]',
                'best': 'best[ext=mp4]/best',
            }
            ydl_opts['format'] = fallback.get(quality, fallback['1080'])

    return ydl_opts


def download_audio(url, output_dir="downloads", ffmpeg_path=None, download_format='mp3', quality='192'):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = build_ydl_opts(output_dir, ffmpeg_path, download_format, quality)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, None
    except Exception as e:
        error_msg = str(e)
        if 'ffmpeg' in error_msg.lower() or 'ffprobe' in error_msg.lower():
            return False, "FFmpeg/ffprobe tidak ditemukan"
        return False, str(e)


def single_download(ffmpeg_path=None, download_format='mp3', quality='192'):
    url = Prompt.ask("\n[bold cyan]Masukkan URL YouTube[/]").strip()
    if not url:
        console.print("[bold red]URL tidak boleh kosong![/]")
        return

    console.print(f"\n[bold]Mendownload:[/] [cyan]{url}[/]")
    success, err = download_audio(url, ffmpeg_path=ffmpeg_path, download_format=download_format, quality=quality)
    if success:
        console.print("[bold green]Download selesai![/]")
    else:
        console.print(f"[bold red]Error:[/] {err}")


def batch_download(ffmpeg_path=None, download_format='mp3', quality='192'):
    file_path = Prompt.ask("\n[bold cyan]Masukkan path file .txt[/]").strip()

    if not os.path.exists(file_path):
        console.print(f"[bold red]Error: File '{file_path}' tidak ditemukan![/]")
        return

    urls = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)

    if not urls:
        console.print("[bold red]Tidak ada URL yang valid dalam file![/]")
        return

    total = len(urls)
    success_count = 0
    console.print(f"\n[bold cyan]Memulai batch {total} download ({CONCURRENT_WORKERS}x parallel)...[/]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]{task.description}[/]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]0/{total} selesai", total=total)

        with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
            fut_map = {
                executor.submit(download_audio, url, ffmpeg_path=ffmpeg_path, download_format=download_format, quality=quality): url
                for url in urls
            }
            for future in as_completed(fut_map):
                url = fut_map[future]
                succ, err = future.result()
                if succ:
                    success_count += 1
                progress.update(task, advance=1,
                                description=f"[cyan]{success_count}/{total} selesai")
                if not succ:
                    console.print(f"  [red]Gagal:[/] {url[:60]}... - {err[:40]}")

    console.print(Panel(
        f"[bold green]Batch selesai! {success_count}/{total} berhasil didownload.[/]"
        if success_count == total else
        f"[bold yellow]Batch selesai! {success_count}/{total} berhasil didownload.[/]",
        border_style="green" if success_count == total else "yellow",
    ))


def select_format_and_quality():
    console.print("\n[bold]Pilih format download:[/]")
    console.print(Panel(
        "[cyan]1.[/] MP3 (Audio only)\n"
        "[cyan]2.[/] MP4 (Video)",
        border_style="blue",
        padding=(1, 2),
    ))
    format_choice = Prompt.ask("Pilih format", choices=["1", "2"], default="1")
    download_format = 'mp3' if format_choice != '2' else 'mp4'

    if download_format == 'mp3':
        console.print("\n[bold]Pilih kualitas MP3:[/]")
        lines = [f"  [cyan]{k}.[/] {v['label']}" for k, v in MP3_QUALITIES.items()]
        console.print(Panel("\n".join(lines), border_style="blue", padding=(1, 2)))
        q_keys = list(MP3_QUALITIES.keys())
        q_choice = Prompt.ask("Pilih kualitas", choices=[str(i + 1) for i in range(len(q_keys))], default="2")
        quality = q_keys[int(q_choice) - 1]
    else:
        console.print("\n[bold]Pilih kualitas MP4:[/]")
        lines = [f"  [cyan]{k}.[/] {v['label']}" for k, v in MP4_QUALITIES.items()]
        console.print(Panel("\n".join(lines), border_style="blue", padding=(1, 2)))
        q_keys = list(MP4_QUALITIES.keys())
        q_choice = Prompt.ask("Pilih kualitas", choices=[str(i + 1) for i in range(len(q_keys))], default="2")
        quality = q_keys[int(q_choice) - 1]

    return download_format, quality


def main():
    ffmpeg_path = check_ffmpeg()
    if ffmpeg_path:
        console.print(f"\n[green]FFmpeg:[/] [cyan]{ffmpeg_path}[/]")
    else:
        console.print("\n[yellow]Berjalan tanpa FFmpeg (fitur MP3/MP4+Audio terbatas)[/]")

    download_format, quality = select_format_and_quality()

    while True:
        show_menu(download_format, quality)
        choice = Prompt.ask("[bold cyan]Pilih menu[/]", choices=["1", "2", "3", "4"])

        if choice == '1':
            single_download(ffmpeg_path, download_format, quality)
        elif choice == '2':
            batch_download(ffmpeg_path, download_format, quality)
        elif choice == '3':
            donasi()
        elif choice == '4':
            console.print("\n[bold green]Keluar program. Terima kasih![/]")
            break


if __name__ == "__main__":
    main()
