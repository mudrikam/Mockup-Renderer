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

- Python 3.8+
- PySide6
- qtawesome
- Adobe Photoshop (versi terbaru)

## Cara Kerja

1. **Pilih Folder dan Pengaturan**
   - Pilih folder berisi file mockup PSD.
   - Pilih folder berisi file desain (PNG, JPG, PSD, dll).
   - Masukkan nama layer smart object di PSD yang ingin diganti.
   - Pilih folder output untuk hasil render.
   - Pilih format output (PNG atau JPG).
   - Aplikasi akan mencoba mendeteksi path Photoshop.exe secara otomatis. Jika gagal, Anda bisa pilih manual.

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

## Cara Penggunaan

1. Jalankan `Launcher.bat` atau `python main.py`
2. Atur path folder:
   - Folder Sumber: Folder berisi file mockup PSD
   - Folder Desain: Folder berisi file desain yang akan diterapkan
   - Smart Object: Nama layer smart object yang akan diganti di mockup
   - Folder Output: Folder untuk menyimpan hasil ekspor
   - Photoshop.exe: Path ke Photoshop (otomatis terdeteksi atau pilih manual)
3. Pilih format output (PNG atau JPG)
4. Klik "Render Mockup" untuk memulai proses batch

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

---

**Penjelasan:**  
Aplikasi ini mengotomatisasi Photoshop untuk batch mengganti smart object di mockup PSD dengan file desain Anda, lalu mengekspor setiap kombinasi sebagai gambar baru. Cocok untuk preview produk, print-on-demand, dan otomasi desain.