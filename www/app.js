function runCommand(action) {
    const urlInput = document.getElementById('urlInput');
    const status = document.getElementById('status');
    const url = urlInput.value.trim();

    if (action !== 'list' && action !== 'clean' && !url) {
        status.innerText = "⚠️ Masukkan link YouTube terlebih dahulu!";
        status.style.color = "#f87171";
        return;
    }

    let command = "";
    if (action === 'transcribe') {
        command = `yt-transcriber transcribe -u "${url}"`;
    } else if (action === 'download') {
        command = `yt-transcriber download -u "${url}"`;
    } else if (action === 'seo') {
        command = `yt-transcriber seo -u "${url}"`;
    } else if (action === 'list') {
        command = `yt-transcriber list`;
    } else if (action === 'clean') {
        // Trik: Otomatis cari file .srt terbaru di folder AI_Captions
        command = `yt-transcriber clean -f $(ls -t ~/storage/downloads/AI_Captions/*.srt 2>/dev/null | head -1)`;
    }

    navigator.clipboard.writeText(command).then(() => {
        status.innerText = `✅ Perintah disalin! Membuka Termux...`;
        status.style.color = "#4ade80";

        setTimeout(() => {
            window.location.href = 'termux://'; 
            setTimeout(() => {
                status.innerText = `📋 Perintah ada di clipboard!\nSilakan Paste di Termux:\n${command}`;
            }, 1000);
        }, 500);
    }).catch(err => {
        status.innerText = "❌ Gagal menyalin ke clipboard.";
        status.style.color = "#f87171";
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('status').innerText = "Siap memproses. Masukkan link YouTube.";
});
