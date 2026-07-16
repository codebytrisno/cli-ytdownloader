#!/usr/bin/env python3
import os
import sys
import shutil
import threading
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed

import customtkinter as ctk
from tkinter import filedialog, messagebox

try:
    import yt_dlp
except ImportError:
    messagebox.showerror("Error", "yt-dlp tidak terinstall.\nJalankan: pip install yt-dlp")
    sys.exit(1)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

MP3_QUALITIES = {
    '128': '128kbps (Cepat)',
    '192': '192kbps (Recommended)',
    '320': '320kbps (High Quality)',
    'vbr0': 'VBR 0 (Terbaik)',
}

MP4_QUALITIES = {
    '720': '720p (HD)',
    '1080': '1080p (Full HD)',
    'best': 'Best (Tertinggi)',
}

CONCURRENT_WORKERS = 3


def find_ffmpeg():
    if shutil.which('ffmpeg'):
        return shutil.which('ffmpeg')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_names = ['ffmpeg', 'ffmpeg.exe']
    common_paths = [
        os.path.join(script_dir, 'ffmpeg', 'bin'),
        os.path.join(os.environ.get('ProgramFiles', ''), 'ffmpeg', 'bin'),
        os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'ffmpeg', 'bin'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages', 'FFmpeg', 'ffmpeg', 'bin'),
    ]
    for path in common_paths:
        for name in ffmpeg_names:
            full_path = os.path.join(path, name)
            if os.path.exists(full_path):
                return full_path
    return None


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


class DownloadThread(threading.Thread):
    def __init__(self, url, output_dir, download_format, ffmpeg_path, quality, finished_callback, progress_callback=None, index=0, total=1):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.download_format = download_format
        self.ffmpeg_path = ffmpeg_path
        self.quality = quality
        self.finished_callback = finished_callback
        self.progress_callback = progress_callback
        self.index = index
        self.total = total
        self.daemon = True

    def run(self):
        os.makedirs(self.output_dir, exist_ok=True)
        ydl_opts = build_ydl_opts(self.output_dir, self.ffmpeg_path, self.download_format, self.quality)

        if self.progress_callback:
            def hook(d):
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                    downloaded = d.get('downloaded_bytes', 0)
                    pct = (downloaded / total * 100) if total > 0 else 0
                    speed = d.get('_speed_str', '?')
                    eta = d.get('_eta_str', '?')
                    self.progress_callback(pct, speed, eta, 'downloading')
                elif d['status'] == 'finished':
                    self.progress_callback(100, '', '', 'processing')
            ydl_opts['progress_hooks'] = [hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished_callback(True, self.url, self.index, self.total, None)
        except Exception as e:
            self.finished_callback(False, self.url, self.index, self.total, str(e))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("640x620")
        self.minsize(600, 560)

        self.ffmpeg_path = find_ffmpeg()
        self.download_format = "mp3"
        self.mp3_quality = "192"
        self.mp4_quality = "1080"
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        os.makedirs(self.output_dir, exist_ok=True)

        self.after(100, self.setup_ui)

    def setup_ui(self):
        header = ctk.CTkLabel(self, text="YouTube Downloader", font=ctk.CTkFont(size=22, weight="bold"))
        header.pack(pady=(15, 2))

        sub = ctk.CTkLabel(self, text="Download video/audio dari YouTube", font=ctk.CTkFont(size=13))
        sub.pack(pady=(0, 8))

        ffmpeg_status = ctk.CTkLabel(
            self,
            text=f"FFmpeg: [TERDETEKSI]" if self.ffmpeg_path else "FFmpeg: [TIDAK DITEMUKAN - fitur terbatas]",
            text_color="#2ecc71" if self.ffmpeg_path else "#e74c3c",
            font=ctk.CTkFont(size=12),
        )
        ffmpeg_status.pack(pady=(0, 10))

        tabview = ctk.CTkTabview(self, width=580, height=440)
        tabview.pack(padx=15, pady=(0, 10), fill="both", expand=True)

        tab_single = tabview.add("Single Download")
        tab_batch = tabview.add("Batch Download")
        tab_settings = tabview.add("Pengaturan")

        self.setup_single_tab(tab_single)
        self.setup_batch_tab(tab_batch)
        self.setup_settings_tab(tab_settings)

    def setup_single_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)

        url_label = ctk.CTkLabel(parent, text="URL YouTube:", anchor="w", font=ctk.CTkFont(size=13))
        url_label.grid(row=0, column=0, sticky="w", padx=10, pady=(15, 2))

        self.url_entry = ctk.CTkEntry(parent, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.single_info = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=11), text_color="gray", anchor="w")
        self.single_info.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))

        self.single_progress = ctk.CTkProgressBar(parent, mode="indeterminate")
        self.single_progress.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 5))
        self.single_progress.set(0)

        self.single_status = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=12))
        self.single_status.grid(row=4, column=0, sticky="w", padx=10, pady=(0, 5))

        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=5, column=0, pady=(5, 15))

        self.single_btn = ctk.CTkButton(btn_frame, text="Download", width=160, command=self.start_single_download)
        self.single_btn.pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="Buka Folder", width=120, command=self.open_downloads).pack(side="left", padx=5)

        self.update_single_info()

    def setup_batch_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)

        file_label = ctk.CTkLabel(parent, text="File .txt berisi URL:", anchor="w", font=ctk.CTkFont(size=13))
        file_label.grid(row=0, column=0, sticky="w", padx=10, pady=(15, 2))

        file_sel_frame = ctk.CTkFrame(parent, fg_color="transparent")
        file_sel_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        file_sel_frame.grid_columnconfigure(0, weight=1)

        self.batch_file_entry = ctk.CTkEntry(file_sel_frame, placeholder_text="Pilih file .txt...")
        self.batch_file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(file_sel_frame, text="Browse", width=80, command=self.browse_file).grid(row=0, column=1)

        self.batch_info = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=11), text_color="gray", anchor="w")
        self.batch_info.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))

        self.batch_progress = ctk.CTkProgressBar(parent, mode="determinate")
        self.batch_progress.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 5))
        self.batch_progress.set(0)

        self.batch_status = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=12))
        self.batch_status.grid(row=4, column=0, sticky="w", padx=10, pady=(0, 5))

        self.batch_detail = ctk.CTkTextbox(parent, height=120, font=ctk.CTkFont(size=11))
        self.batch_detail.grid(row=5, column=0, sticky="ew", padx=10, pady=(5, 5))

        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=6, column=0, pady=(5, 15))

        self.batch_btn = ctk.CTkButton(btn_frame, text="Mulai Batch", width=160, command=self.start_batch_download)
        self.batch_btn.pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="Buka Folder", width=120, command=self.open_downloads).pack(side="left", padx=5)

        self.update_batch_info()

    def setup_settings_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)

        fmt_label = ctk.CTkLabel(parent, text="Format Download:", font=ctk.CTkFont(size=14, weight="bold"))
        fmt_label.grid(row=0, column=0, sticky="w", padx=10, pady=(15, 5))

        self.format_var = ctk.StringVar(value="mp3")
        mp3_radio = ctk.CTkRadioButton(parent, text="MP3 (Audio)", variable=self.format_var, value="mp3", command=self.on_format_change)
        mp3_radio.grid(row=1, column=0, sticky="w", padx=20, pady=2)
        mp4_radio = ctk.CTkRadioButton(parent, text="MP4 (Video + Audio)", variable=self.format_var, value="mp4", command=self.on_format_change)
        mp4_radio.grid(row=2, column=0, sticky="w", padx=20, pady=2)

        sep = ctk.CTkFrame(parent, height=1, fg_color="gray")
        sep.grid(row=3, column=0, sticky="ew", padx=10, pady=12)

        q_label = ctk.CTkLabel(parent, text="Kualitas:", font=ctk.CTkFont(size=14, weight="bold"))
        q_label.grid(row=4, column=0, sticky="w", padx=10, pady=(0, 5))

        self.mp3_q_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.mp3_q_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.mp3_q_frame.grid_columnconfigure(0, weight=1)

        self.mp3_quality_var = ctk.StringVar(value="192")
        self.mp3_combo = ctk.CTkComboBox(
            self.mp3_q_frame, values=list(MP3_QUALITIES.values()),
            command=self.on_mp3_quality_change, width=300,
        )
        self.mp3_combo.pack(side="left", padx=5)
        self.mp3_combo.set(MP3_QUALITIES["192"])

        self.mp4_q_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.mp4_q_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.mp4_q_frame.grid_columnconfigure(0, weight=1)

        self.mp4_quality_var = ctk.StringVar(value="1080")
        self.mp4_combo = ctk.CTkComboBox(
            self.mp4_q_frame, values=list(MP4_QUALITIES.values()),
            command=self.on_mp4_quality_change, width=300,
        )
        self.mp4_combo.pack(side="left", padx=5)
        self.mp4_combo.set(MP4_QUALITIES["1080"])

        parallel_label = ctk.CTkLabel(parent, text=f"Parallel Batch: {CONCURRENT_WORKERS}x download", font=ctk.CTkFont(size=12), text_color="gray")
        parallel_label.grid(row=7, column=0, sticky="w", padx=20, pady=(2, 5))

        self._toggle_quality_frames()

        sep2 = ctk.CTkFrame(parent, height=1, fg_color="gray")
        sep2.grid(row=8, column=0, sticky="ew", padx=10, pady=12)

        dir_label = ctk.CTkLabel(parent, text="Folder Download:", font=ctk.CTkFont(size=14, weight="bold"))
        dir_label.grid(row=9, column=0, sticky="w", padx=10, pady=(0, 5))

        dir_frame = ctk.CTkFrame(parent, fg_color="transparent")
        dir_frame.grid(row=10, column=0, sticky="ew", padx=10, pady=(0, 10))
        dir_frame.grid_columnconfigure(0, weight=1)

        self.dir_label = ctk.CTkLabel(dir_frame, text=self.output_dir, font=ctk.CTkFont(size=11), text_color="gray", anchor="w")
        self.dir_label.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(dir_frame, text="Ganti", width=80, command=self.change_output_dir).grid(row=0, column=1)

        sep3 = ctk.CTkFrame(parent, height=1, fg_color="gray")
        sep3.grid(row=11, column=0, sticky="ew", padx=10, pady=12)

        donasi_btn = ctk.CTkButton(parent, text="Donasi", width=120, fg_color="#e74c3c", hover_color="#c0392b", command=self.open_donasi)
        donasi_btn.grid(row=12, column=0, padx=10, pady=5)

    def _toggle_quality_frames(self):
        is_mp3 = self.format_var.get() == "mp3"
        if is_mp3:
            self.mp3_q_frame.grid()
            self.mp4_q_frame.grid_remove()
        else:
            self.mp3_q_frame.grid_remove()
            self.mp4_q_frame.grid()

    def on_format_change(self):
        self.download_format = self.format_var.get()
        self._toggle_quality_frames()
        self.update_single_info()
        self.update_batch_info()

    def on_mp3_quality_change(self, choice):
        rev = {v: k for k, v in MP3_QUALITIES.items()}
        self.mp3_quality = rev.get(choice, '192')
        self.update_single_info()
        self.update_batch_info()

    def on_mp4_quality_change(self, choice):
        rev = {v: k for k, v in MP4_QUALITIES.items()}
        self.mp4_quality = rev.get(choice, '1080')
        self.update_single_info()
        self.update_batch_info()

    def get_current_quality_label(self):
        if self.download_format == 'mp3':
            return MP3_QUALITIES.get(self.mp3_quality, self.mp3_quality)
        else:
            return MP4_QUALITIES.get(self.mp4_quality, self.mp4_quality)

    def update_single_info(self):
        q = self.get_current_quality_label()
        fmt = "MP3" if self.download_format == 'mp3' else "MP4"
        self.single_info.configure(text=f"Format: {fmt} | Kualitas: {q}")

    def update_batch_info(self):
        q = self.get_current_quality_label()
        fmt = "MP3" if self.download_format == 'mp3' else "MP4"
        self.batch_info.configure(text=f"Format: {fmt} | Kualitas: {q} | Parallel: {CONCURRENT_WORKERS}x")

    def change_output_dir(self):
        path = filedialog.askdirectory(initialdir=self.output_dir, title="Pilih folder download")
        if path:
            self.output_dir = path
            self.dir_label.configure(text=path)

    def browse_file(self):
        path = filedialog.askopenfilename(title="Pilih file .txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.batch_file_entry.delete(0, "end")
            self.batch_file_entry.insert(0, path)

    def open_downloads(self):
        os.makedirs(self.output_dir, exist_ok=True)
        if sys.platform == "darwin":
            os.system(f'open "{self.output_dir}"')
        elif sys.platform == "win32":
            os.startfile(self.output_dir)
        else:
            try:
                import subprocess
                subprocess.Popen(['xdg-open', self.output_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                self.batch_status.configure(text="Error: xdg-open tidak ditemukan. Buka manual foldernya.")

    def open_donasi(self):
        webbrowser.open("https://sociabuzz.com/trisnosanjaya")

    def start_single_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Peringatan", "URL tidak boleh kosong!")
            return

        self.single_btn.configure(state="disabled", text="Downloading...")
        self.single_progress.configure(mode="determinate")
        self.single_progress.set(0)
        self.single_status.configure(text=f"Mendownload: {url[:50]}...", text_color="white")

        quality = self.mp3_quality if self.download_format == 'mp3' else self.mp4_quality

        def on_progress(pct, speed, eta, status):
            self.after(0, lambda: self._update_single_progress(pct, speed, eta, status))

        DownloadThread(
            url, self.output_dir, self.download_format, self.ffmpeg_path, quality,
            finished_callback=self.single_finished,
            progress_callback=on_progress,
        ).start()

    def _update_single_progress(self, pct, speed, eta, status):
        self.single_progress.set(pct / 100)
        if status == 'processing':
            self.single_status.configure(text="Memproses audio... (FFmpeg)")
        else:
            self.single_status.configure(text=f"{pct:.1f}% | {speed} | ETA {eta}")

    def single_finished(self, success, url, *args):
        self.after(0, lambda: self._single_finished_ui(success, url, args))

    def _single_finished_ui(self, success, url, args):
        self.single_progress.set(1 if success else 0)
        self.single_btn.configure(state="normal", text="Download")

        if success:
            self.single_status.configure(text="Selesai! File tersimpan di folder downloads/.", text_color="#2ecc71")
        else:
            err = args[-1] if len(args) > 2 and args[-1] else "Unknown error"
            self.single_status.configure(text=f"Gagal: {err[:60]}", text_color="#e74c3c")

    def start_batch_download(self):
        file_path = self.batch_file_entry.get().strip()
        if not file_path or not os.path.exists(file_path):
            messagebox.showwarning("Peringatan", "File tidak ditemukan!")
            return

        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        if not urls:
            messagebox.showwarning("Peringatan", "Tidak ada URL valid dalam file!")
            return

        self.total_batch = len(urls)
        self.batch_success = 0

        self.batch_btn.configure(state="disabled", text="Memproses...")
        self.batch_progress.configure(mode="determinate")
        self.batch_progress.set(0)
        self.batch_detail.delete("0.0", "end")
        self.batch_detail.insert("end", f"Memulai batch {self.total_batch} download ({CONCURRENT_WORKERS}x parallel)...\n")
        self.batch_status.configure(text=f"0/{self.total_batch} selesai")

        self._run_parallel_batch(urls)

    def _run_parallel_batch(self, urls):
        quality = self.mp3_quality if self.download_format == 'mp3' else self.mp4_quality
        self._batch_progress_lines = {}

        def on_item_progress(idx, pct, speed, eta, status):
            self.after(0, lambda: self._update_batch_item_progress(idx, pct, speed, eta, status))

        def on_item_done(success, url, idx, total, error):
            self.after(0, lambda: self._batch_item_done(success, url, idx, total, error))

        def worker(url, idx, total):
            t = DownloadThread(
                url, self.output_dir, self.download_format, self.ffmpeg_path, quality,
                finished_callback=lambda s, u, i, t, e: on_item_done(s, u, i, t, e),
                progress_callback=lambda p, s, e, st: on_item_progress(idx, p, s, e, st),
                index=idx, total=total,
            )
            t.run()

        threading.Thread(target=self._batch_worker, args=(urls, worker), daemon=True).start()

    def _update_batch_item_progress(self, idx, pct, speed, eta, status):
        line_num = self._batch_progress_lines.get(idx)
        if line_num is None:
            self.batch_detail.insert("end", f"[#{idx+1}] 0% | ...\n")
            self._batch_progress_lines[idx] = int(self.batch_detail.index("end-1c").split('.')[0])
            line_num = self._batch_progress_lines[idx]

        if status == 'processing':
            text = f"[#{idx+1}] Memproses audio... (FFmpeg)\n"
        else:
            text = f"[#{idx+1}] {pct:.1f}% | {speed} | ETA {eta}\n"

        self.batch_detail.delete(f"{line_num}.0", f"{line_num}.0 lineend")
        self.batch_detail.insert(f"{line_num}.0", text)
        self.batch_detail.see("end")

    def _batch_worker(self, urls, worker_fn):
        total = len(urls)
        with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
            fut_map = {
                executor.submit(worker_fn, url, idx, total): (url, idx)
                for idx, url in enumerate(urls)
            }
            for future in as_completed(fut_map):
                pass

        self.after(0, self._batch_all_done)

    def _batch_item_done(self, success, url, idx, total, error):
        self.batch_success += 1 if success else 0
        done = int(self.batch_progress.get() * total) + 1

        line_num = self._batch_progress_lines.get(idx)
        if line_num:
            if success:
                self.batch_detail.delete(f"{line_num}.0", f"{line_num}.0 lineend")
                self.batch_detail.insert(f"{line_num}.0", f"[#{idx+1}] [OK] {url[:40]}...\n")
            else:
                err = error or "Unknown"
                self.batch_detail.delete(f"{line_num}.0", f"{line_num}.0 lineend")
                self.batch_detail.insert(f"{line_num}.0", f"[#{idx+1}] [FAIL] {url[:40]}... - {err[:30]}\n")

        self.batch_detail.see("end")
        self.batch_progress.set(done / total)
        self.batch_status.configure(text=f"{done}/{total} selesai")

    def _batch_all_done(self):
        total = self.total_batch
        self.batch_btn.configure(state="normal", text="Mulai Batch")
        color = "#2ecc71" if self.batch_success == total else "#e74c3c"
        self.batch_status.configure(
            text=f"Batch selesai! {self.batch_success}/{total} berhasil.",
            text_color=color,
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()
