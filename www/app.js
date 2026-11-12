// Fungsi utama untuk memproses perintah
function runCommand(action) {
    const urlInput = document.getElementById('urlInput');
    const status = document.getElementById('status');
    const url = urlInput.value.trim();

    // Validasi input (kecuali untuk tombol 'Lihat File')
    if (action !== 'list' && !url) {
        status.innerText = "⚠️ Masukkan link YouTube terlebih dahulu!";
        status.style.color = "#f87171";
        return;
    }

    // Siapkan perintah Termux
    let command = "";
    if (action === 'transcribe') {
        command = `yt-transcriber transcribe -u "${url}"`;
    } else if (action === 'download') {
        command = `yt-transcriber download -u "${url}"`;
    } else if (action === 'seo') {
        command = `yt-transcriber seo -u "${url}"`;
    } else if (action === 'list') {
        command = `yt-transcriber list`;
    }

    // 1. Salin perintah ke Clipboard
    navigator.clipboard.writeText(command).then(() => {
        status.innerText = `✅ Perintah disalin! Membuka Termux...`;
        status.style.color = "#4ade80";

        // 2. Buka aplikasi Termux setelah jeda singkat
        setTimeout(() => {
            // Mencoba membuka Termux via URL scheme
            window.location.href = 'termux://'; 
            
            // Fallback jika scheme tidak bekerja (opsional)
            setTimeout(() => {
                status.innerText = `📋 Perintah ada di clipboard!\nSilakan Paste di Termux:\n${command}`;
            }, 1000);
        }, 500);
    }).catch(err => {
        status.innerText = "❌ Gagal menyalin ke clipboard.";
        status.style.color = "#f87171";
    });
}

// Inisialisasi status awal
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('status').innerText = "Siap memproses. Masukkan link YouTube.";
});
