"""
YT-Transcriber Pro: Professional AI Transcription & SEO Tool.
"""
import click
import subprocess
import os
import json
import re
import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.logging import RichHandler

# Setup Logging Profesional
logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("yt-transcriber")
console = Console()

# Konfigurasi Default
WHISPER_BIN = os.path.expanduser("~/whisper.cpp/build/bin/whisper-cli")
WHISPER_MODEL = os.path.expanduser("~/whisper.cpp/models/ggml-base.bin")
OUTPUT_DIR = os.path.expanduser("~/storage/downloads/AI_Captions")

def check_dependencies() -> None:
    """Cek apakah dependensi dan folder sudah siap."""
    if not os.path.exists(WHISPER_BIN):
        log.error("whisper.cpp tidak ditemukan. Jalankan install.sh dulu!")
        raise click.Abort()
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output untuk debugging.')
@click.version_option(version='1.0.0', prog_name='YT-Transcriber Pro')
def cli(verbose: bool) -> None:
    """🎬 YT-Transcriber Pro: Tools AI Transkrip & SEO untuk Konten Kreator."""
    if verbose:
        log.setLevel(logging.DEBUG)
        log.debug("Verbose mode diaktifkan.")
    else:
        log.setLevel(logging.WARNING)

@cli.command()
@click.option('--url', '-u', prompt='Masukkan Link YouTube', help='Link video YouTube')
@click.option('--lang', '-l', default='id', help='Bahasa subtitle (id/en)')
def download(url: str, lang: str) -> None:
    """Download subtitle langsung dari YouTube (Cepat)."""
    check_dependencies()
    console.print(Panel(f"Mencoba download subtitle: [bold cyan]{url}[/bold cyan]", title="📥 Download Subtitle"))
    
    cmd = [
        "yt-dlp", "--write-auto-subs", "--sub-langs", lang, 
        "--convert-subs", "srt", "--skip-download",
        "-o", f"{OUTPUT_DIR}/%(title)s.%(ext)s", url
    ]
    
    log.debug(f"Menjalankan command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, capture_output=not verbose)
        console.print("[bold green]✅ Sukses! File ada di folder AI_Captions.[/bold green]")
    except subprocess.CalledProcessError as e:
        log.error(f"Gagal download subtitle: {e}")
        console.print("[bold red]❌ Gagal download subtitle. Coba gunakan perintah 'transcribe'.[/bold red]")

@cli.command()
@click.option('--url', '-u', prompt='Masukkan Link YouTube', help='Link video YouTube')
@click.option('--lang', '-l', default='auto', help='Bahasa transkrip (auto/id/en). Default: auto detect bahasa asli')
def transcribe(url: str, lang: str) -> None:
    """Download audio & buat transkrip otomatis pakai AI (Mendeteksi bahasa asli)."""
    check_dependencies()
    console.print(Panel(f"Memproses video dengan AI: [bold cyan]{url}[/bold cyan]", title="🧠 AI Transcribe"))

    # 1. Download Audio
    console.print("[yellow]⬇️  Step 1: Mendownload audio...[/yellow]")
    dl_cmd = [
        "yt-dlp", "-x", "--audio-format", "wav",
        "-o", os.path.expanduser("~/storage/downloads/%(title)s.%(ext)s"), url
    ]
    log.debug(f"Download command: {' '.join(dl_cmd)}")
    subprocess.run(dl_cmd, check=True)

    # 2. Run Whisper
    console.print("[yellow]🎙️  Step 2: AI sedang mendengarkan & mendeteksi bahasa...[/yellow]")
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Processing audio...", total=None)
        
        whisper_cmd = [
            WHISPER_BIN, "-m", WHISPER_MODEL, 
            "-f", os.path.expanduser("~/storage/downloads/*.wav"), 
            "-osrt"
        ]
        
        if lang.lower() != 'auto':
            whisper_cmd.extend(["-l", lang])
            
        full_cmd = " ".join(whisper_cmd)
        log.debug(f"Whisper command: {full_cmd}")
        subprocess.run(full_cmd, shell=True, cwd=os.path.expanduser("~/storage/downloads/"))
        progress.update(task, completed=True)

    # 3. Pindahkan & Bersihkan
    console.print("[yellow]📁 Step 3: Merapikan file...[/yellow]")
    subprocess.run(f"mv ~/storage/downloads/*.srt {OUTPUT_DIR}/", shell=True)
    subprocess.run("rm -f ~/storage/downloads/*.wav", shell=True)
    
    console.print("[bold green]🎉 Selesai! Transkrip bahasa asli tersimpan di AI_Captions.[/bold green]")

@cli.command(name='list')
def list_files() -> None:
    """Lihat daftar file transkrip yang sudah dibuat."""
    check_dependencies()
    table = Table(title="📂 File di AI_Captions")
    table.add_column("Nama File", style="cyan")
    table.add_column("Ukuran", style="green")
    
    files_found = False
    for f in sorted(Path(OUTPUT_DIR).iterdir(), key=os.path.getmtime, reverse=True):
        if f.suffix in ['.srt', '.txt']:
            size_kb = f.stat().st_size / 1024
            table.add_row(f.name, f"{size_kb:.1f} KB")
            files_found = True
            
    if not files_found:
        console.print("[yellow]Folder AI_Captions masih kosong.[/yellow]")
    else:
        console.print(table)

@cli.command()
@click.option('--url', '-u', prompt='Masukkan Link YouTube', help='Link video YouTube untuk analisis SEO')
def seo(url: str) -> None:
    """Analisis SEO video YouTube (Tags, Hashtag, Metadata, Score)."""
    console.print(Panel(f"Menganalisis SEO: [bold cyan]{url}[/bold cyan]", title="🔍 SEO Analyzer"))
    console.print("[yellow]📊 Mengambil metadata video...[/yellow]")
    
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", url],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        
        console.print("\n[bold blue]📌 INFORMASI DASAR[/bold blue]")
        console.print(f"Judul: [green]{data.get('title', 'N/A')}[/green]")
        console.print(f"Channel: [cyan]{data.get('uploader', 'N/A')}[/cyan]")
        console.print(f"Durasi: {data.get('duration_string', 'N/A')} | Views: {data.get('view_count', 0):,} | Upload: {data.get('upload_date', 'N/A')}")
        
        tags = data.get('tags', [])
        if tags:
            console.print(f"\n[bold blue]🏷️  TAGS ({len(tags)} ditemukan)[/bold blue]")
            for i, tag in enumerate(tags[:15], 1):
                console.print(f"  {i}. [yellow]{tag}[/yellow]")
            if len(tags) > 15:
                console.print(f"  ... dan {len(tags) - 15} tags lainnya")
        else:
            console.print("\n[red]⚠️  Video tidak memiliki tags[/red]")
        
        description = data.get('description', '') or ''
        hashtags = re.findall(r'#\w+', description)
        if hashtags:
            console.print(f"\n[bold blue]#️⃣  HASHTAGS ({len(hashtags)} ditemukan)[/bold blue]")
            for tag in list(set(hashtags))[:10]:
                console.print(f"  • [magenta]{tag}[/magenta]")
        else:
            console.print("\n[red]⚠️  Tidak ada hashtag di deskripsi[/red]")
        
        console.print(f"\n[bold blue]📈 ANALISIS SEO SEDERHANA[/bold blue]")
        score = 0
        
        if len(tags) >= 10: score += 30; console.print("  ✅ Tags optimal (10+ tags) [+30]")
        elif len(tags) >= 5: score += 15; console.print("  ⚠️ Tags cukup (5-9 tags) [+15]")
        else: console.print("  ❌ Tags kurang (< 5 tags) [0]")
            
        if len(hashtags) >= 3: score += 20; console.print("  ✅ Hashtag optimal (3+ hashtags) [+20]")
        elif len(hashtags) >= 1: score += 10; console.print("  ⚠️ Hashtag cukup (1-2 hashtags) [+10]")
        else: console.print("  ❌ Tidak ada hashtag [0]")
            
        if len(description) >= 200: score += 25; console.print("  ✅ Deskripsi panjang (200+ karakter) [+25]")
        else: console.print("  ❌ Deskripsi terlalu pendek [0]")
            
        title_len = len(data.get('title', ''))
        if 50 <= title_len <= 70: score += 25; console.print("  ✅ Panjang judul optimal (50-70 karakter) [+25]")
        else: console.print(f"  ⚠️ Panjang judul: {title_len} karakter (ideal: 50-70) [0]")
            
        console.print(f"\n[bold]🎯 TOTAL SEO SCORE: {score}/100[/bold]")
        if score >= 80: console.print("[bold green]⭐ Video ini SEO-nya sangat baik![/bold green]")
        elif score >= 50: console.print("[bold yellow]⚠️ Video ini SEO-nya cukup, bisa ditingkatkan[/bold yellow]")
        else: console.print("[bold red]❌ Video ini SEO-nya perlu perbaikan serius[/bold red]")
        
        video_id = data.get('id', 'unknown')
        save_file = f"{OUTPUT_DIR}/seo_analysis_{video_id}.txt"
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(f"SEO Analysis: {data.get('title')}\n")
            f.write(f"Channel: {data.get('uploader')}\n")
            f.write(f"Tags: {', '.join(tags)}\n")
            f.write(f"Hashtags: {', '.join(list(set(hashtags)))}\n")
            f.write(f"SEO Score: {score}/100\n")
        console.print(f"\n[green]💾 Hasil analisis tersimpan di: {save_file}[/green]")
        
    except subprocess.CalledProcessError:
        console.print("[bold red]❌ Error: Gagal mengambil metadata. Pastikan link YouTube valid.[/bold red]")
    except json.JSONDecodeError:
        console.print("[bold red]❌ Error: Gagal membaca data dari YouTube.[/bold red]")
    except Exception as e:
        log.exception("Terjadi error tidak terduga")
        console.print(f"[bold red]❌ Error Tidak Terduga: {str(e)}[/bold red]")

if __name__ == '__main__':
    cli()
