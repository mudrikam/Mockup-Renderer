import sys
import subprocess
import os
import time
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QMessageBox, QLabel, 
                             QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
import qtawesome as qta
import datetime

class MockupRenderer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mockup Renderer")
        self.resize(800, 500)  # Increased size to accommodate table
        self.setup_ui()
        
    def setup_ui(self):
        # Layout utama
        main_layout = QVBoxLayout()
        
        # Label instruksi
        self.label = QLabel("Masukkan path atau pilih direktori:")
        main_layout.addWidget(self.label)
        
        # Layout untuk input path dan tombol browse
        path_layout = QHBoxLayout()
        
        # Input path
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Path direktori...")
        self.path_input.textChanged.connect(self.update_file_table)
        path_layout.addWidget(self.path_input, 3)
        
        # Tombol browse dengan icon solid
        browse_icon = qta.icon('fa6s.folder-open', color='#3498db')
        self.browse_button = QPushButton(browse_icon, "")
        self.browse_button.setToolTip("Browse Direktori")
        self.browse_button.clicked.connect(self.browse_directory)
        path_layout.addWidget(self.browse_button)
        
        main_layout.addLayout(path_layout)
        
        # Tabel untuk menampilkan daftar file PSD
        self.file_table = QTableWidget(0, 4)  # 0 row, 4 columns initially
        self.file_table.setHorizontalHeaderLabels(["Nama File", "Ukuran (KB)", "Terakhir Diubah", "Path Lengkap"])
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Nama file stretch
        self.file_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Path stretch
        self.file_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.file_table)
        
        # Informasi total file
        self.info_label = QLabel("0 file PSD ditemukan")
        main_layout.addWidget(self.info_label)
        
        # Tombol open path dengan Photoshop secara otomatis
        open_icon = qta.icon('fa6s.images', color='#2ecc71')
        self.open_button = QPushButton(open_icon, " Render Mockup")
        self.open_button.clicked.connect(self.open_path_in_photoshop)
        main_layout.addWidget(self.open_button)
        
        self.setLayout(main_layout)
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Pilih Direktori")
        if directory:
            self.path_input.setText(directory)
    
    def update_file_table(self):
        path = self.path_input.text().strip()
        self.file_table.setRowCount(0)
        
        if not path or not os.path.exists(path):
            self.info_label.setText("0 file PSD ditemukan")
            return
            
        try:
            psd_files = []
            for file in os.listdir(path):
                if file.lower().endswith(".psd"):
                    file_path = os.path.join(path, file)
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    mod_time = os.path.getmtime(file_path)
                    mod_time_str = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                    
                    psd_files.append({
                        "name": file,
                        "size": file_size,
                        "modified": mod_time_str,
                        "path": file_path
                    })
            
            # Sort by name
            psd_files.sort(key=lambda x: x["name"])
            
            # Add files to table
            self.file_table.setRowCount(len(psd_files))
            for i, file_info in enumerate(psd_files):
                self.file_table.setItem(i, 0, QTableWidgetItem(file_info["name"]))
                self.file_table.setItem(i, 1, QTableWidgetItem(f"{file_info['size']:.2f}"))
                self.file_table.setItem(i, 2, QTableWidgetItem(file_info["modified"]))
                self.file_table.setItem(i, 3, QTableWidgetItem(file_info["path"]))
                
            self.info_label.setText(f"{len(psd_files)} file PSD ditemukan")
        except Exception as e:
            self.info_label.setText(f"Error: {str(e)}")
    
    def open_path_in_photoshop(self):
        path = self.path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "Warning", "Mohon masukkan path direktori terlebih dahulu.")
            return
            
        if not os.path.exists(path):
            QMessageBox.warning(self, "Warning", "Path tidak valid atau tidak ditemukan.")
            return
            
        try:
            ps_exe = self.find_photoshop()
            if not ps_exe:
                QMessageBox.critical(self, "Error", "Photoshop executable tidak ditemukan.")
                return
                
            # Konversi path dengan forward slash untuk ExtendScript
            safe_path = path.replace("\\", "/")
            
            # Pastikan direktori script ada
            script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script")
            os.makedirs(script_dir, exist_ok=True)
            
            # Buat script JSX untuk membuka path
            jsx_path = os.path.join(script_dir, "open_psd.jsx")
            jsx_code = f'''
// Script untuk membuka path di Photoshop
var path = new Folder("{safe_path}");
var files = path.getFiles("*.psd");

if (files.length > 0) {{
    for (var i = 0; i < files.length; i++) {{
        app.open(files[i]);
    }}
    alert("Opened " + files.length + " PSD files from " + path);
}} else {{
    alert("No PSD files found in " + path);
}}
'''
            
            with open(jsx_path, "w", encoding="utf-8") as f:
                f.write(jsx_code)
                
            # Jalankan Photoshop tanpa menunggu output
            subprocess.Popen([ps_exe, "-r", jsx_path], 
                           shell=True, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Tampilkan sukses tanpa memperhatikan exit code
            QMessageBox.information(self, "Sukses", "Perintah render mockup berhasil dikirim ke Photoshop.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menjalankan skrip Photoshop:\n{str(e)}")

    def find_photoshop(self):
        # Program Files locations
        program_files_paths = [
            os.environ.get("ProgramFiles", r"C:\Program Files"),
            os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        ]
        
        # Possible year versions and custom paths
        ps_years = ["2025", "2024", "2023", "2022", "2021", "2020", "CC 2019", "CC 2018", "CC 2017"]
        
        # Check standard Adobe installation paths
        for base_path in program_files_paths:
            for year in ps_years:
                possible_path = os.path.join(base_path, "Adobe", f"Adobe Photoshop {year}", "Photoshop.exe")
                if os.path.exists(possible_path):
                    return possible_path
        
        # Additional common paths where Photoshop might be installed
        additional_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "Adobe", "Adobe Photoshop", "Photoshop.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Adobe", "Adobe Photoshop", "Photoshop.exe")
        ]
        
        for path in additional_paths:
            if os.path.exists(path):
                return path
                
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set aplikasi style
    app.setStyle("Fusion")
    
    window = MockupRenderer()
    window.show()
    sys.exit(app.exec())
