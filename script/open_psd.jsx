// Script template for opening PSD files in Photoshop
// This file will be dynamically generated with the correct path when the application runs

var path = new Folder("");
var files = path.getFiles("*.psd");

if (files.length > 0) {
    for (var i = 0; i < files.length; i++) {
        app.open(files[i]);
    }
    alert("Opened " + files.length + " PSD files from " + path);
} else {
    alert("No PSD files found in " + path);
}