// Script untuk membuka file PSD di Photoshop
// File ini akan dibuat secara dinamis saat aplikasi berjalan

var path = new Folder("");
var files = path.getFiles("*.psd");

if (files.length > 0) {
    for (var i = 0; i < files.length; i++) {
        app.open(files[i]);
    }
    alert("Berhasil membuka " + files.length + " file PSD dari folder " + path);
} else {
    alert("Tidak ditemukan file PSD di folder " + path);
}