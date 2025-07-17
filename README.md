# Mockup-Renderer

Aplikasi PySide6 canggih untuk batch rendering mockup PSD dengan mengganti smart object menggunakan file desain dan mengekspor ke berbagai format.

## Fitur

- Pilih dan telusuri folder berisi file mockup PSD
- Pilih folder desain yang akan diterapkan ke setiap mockup
- Ganti smart object di setiap mockup dengan setiap desain
- Ekspor otomatis ke format PNG atau JPG
- Progress bar visual dan status proses detail
- Jendela selalu di atas untuk monitoring mudah
- Mendukung batch (setiap mockup diproses dengan semua desain)
- Struktur output rapi dengan penomoran file di dalam folder sesuai nama PSD

## Kebutuhan

- Python 3.8+ (disarankan Python 3.12)
- PySide6
- qtawesome
- Adobe Photoshop (versi terbaru, Windows)

## Cara Install

1. **Install Python**
   - Download dan install Python dari [python.org](https://www.python.org/downloads/).
   - Pastikan saat instalasi, opsi "Add Python to PATH" dicentang.

2. **Download Source Code**
   - Download atau clone repository ini ke komputer Anda.

3. **Buka Command Prompt / Terminal**
   - Arahkan ke folder project hasil ekstrak/clone.

4. **Install Dependency**
   Jalankan perintah berikut:
   ```
   pip install PySide6 qtawesome
   ```

5. **Pastikan Photoshop Terinstal**
   - Aplikasi ini membutuhkan Adobe Photoshop yang sudah terinstal di Windows.

## Cara Penggunaan

1. Jalankan aplikasi:
   - Klik dua kali `Launcher.bat` (jika tersedia), atau
   - Jalankan di terminal:
     ```
     python main.py
     ```

2. Isi semua pengaturan pada aplikasi:
   - **Folder Sumber PSD:** Pilih folder berisi file mockup PSD.
   - **Folder Desain:** Pilih folder berisi file desain (PNG, JPG, PSD, dsb).
   - **Target Smart Object:** Masukkan nama layer smart object yang ingin diganti (harus sama persis dengan di PSD).
   - **Folder Output:** Pilih folder untuk menyimpan hasil render.
   - **Format Output:** Pilih PNG atau JPG.
   - **Lokasi Photoshop.exe:** Akan terisi otomatis jika terdeteksi. Jika tidak, klik tombol folder di kanan dan pilih file `Photoshop.exe` secara manual.

3. Klik **Render Mockup** untuk memulai proses batch.

4. Progress bar dan status akan tampil selama proses berjalan. Anda bisa membatalkan proses kapan saja dengan tombol **Batal**.

## Cara Kerja

1. **Pilih Folder dan Pengaturan**
   - Pilih folder mockup PSD, folder desain, nama smart object, folder output, format output, dan path Photoshop.exe.

2. **Proses Batch Rendering**
   - Untuk setiap file mockup PSD:
     - Buka PSD di Photoshop.
     - Untuk setiap file desain:
       - Ganti smart object sesuai nama dengan desain.
       - Ekspor hasilnya sebagai gambar (PNG/JPG) ke subfolder sesuai nama PSD.
       - Ulangi untuk semua desain.
     - Setelah semua desain selesai untuk satu PSD, file PSD ditutup tanpa menyimpan perubahan.

3. **Progress dan Status**
   - Aplikasi menampilkan progress bar dan status proses setiap langkah.
   - Proses bisa dibatalkan kapan saja.

4. **Struktur Output**
   - Folder output berisi subfolder untuk setiap mockup PSD.
   - Setiap subfolder berisi gambar hasil ekspor, dinamai dengan nama PSD dan nomor urut (misal: `mockup1_1.png`, `mockup1_2.png`, ...).

## Struktur Output

Program akan membuat struktur output yang rapi:
- Setiap mockup PSD mendapat subfolder sendiri di folder output.
- Setiap desain yang diterapkan diekspor sebagai gambar terpisah dengan nama unik.

## Contoh

Misal Anda punya:
- 2 mockup PSD: `shirt.psd`, `mug.psd`
- 3 file desain: `design1.png`, `design2.png`, `design3.png`

Setelah proses batch, folder output Anda akan seperti:

```
output/
├── shirt/
│   ├── shirt_1.png
│   ├── shirt_2.png
│   └── shirt_3.png
└── mug/
    ├── mug_1.png
    ├── mug_2.png
    └── mug_3.png
```

## Catatan

- Pastikan Photoshop sudah terinstal dan path Photoshop.exe benar.
- Nama layer smart object harus persis sama dengan di file PSD Anda.
- Aplikasi tidak mengubah file PSD atau desain asli Anda.
- Jika Photoshop tidak terdeteksi otomatis, pilih manual file `Photoshop.exe` (biasanya di `C:\Program Files\Adobe\Adobe Photoshop <versi>\Photoshop.exe`).

---

**Penjelasan:**  
Aplikasi ini mengotomatisasi Photoshop untuk batch mengganti smart object di mockup PSD dengan file desain Anda, lalu mengekspor setiap kombinasi sebagai gambar baru. Cocok untuk preview produk, print-on-demand, dan otomasi desain.