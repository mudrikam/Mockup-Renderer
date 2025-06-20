import sys
import subprocess
import os
import time
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QMessageBox, QLabel, 
                             QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox, QFormLayout, QProgressBar, QSplitter, QComboBox)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta
import datetime

class MockupRenderer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mockup Renderer")
        self.resize(1200, 650)  # Wider to accommodate both tables
        self.setup_ui()
        
    def setup_ui(self):
        # Layout utama
        main_layout = QVBoxLayout()
        
        # Form untuk input paths
        path_group = QGroupBox("Pengaturan")
        path_form = QFormLayout()
        
        # Icon untuk browse buttons
        browse_icon = qta.icon('fa6s.folder-open', color='#3498db')
        
        # 1. Source Directory (Main Directory)
        source_path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Masukkan lokasi folder sumber mockup...")
        self.path_input.textChanged.connect(self.update_file_table)
        source_path_layout.addWidget(self.path_input)
        
        self.browse_button = QPushButton(browse_icon, "")
        self.browse_button.setToolTip("Cari Folder Sumber")
        self.browse_button.clicked.connect(self.browse_directory)
        source_path_layout.addWidget(self.browse_button)
        
        path_form.addRow("Folder Sumber:", source_path_layout)
        
        # 2. Design Directory
        design_dir_layout = QHBoxLayout()
        self.design_dir_input = QLineEdit()
        self.design_dir_input.setPlaceholderText("Masukkan lokasi folder desain...")
        self.design_dir_input.textChanged.connect(self.update_design_table)
        design_dir_layout.addWidget(self.design_dir_input)
        
        self.design_dir_browse = QPushButton(browse_icon, "")
        self.design_dir_browse.setToolTip("Cari Folder Desain")
        self.design_dir_browse.clicked.connect(self.browse_design_dir)
        design_dir_layout.addWidget(self.design_dir_browse)
        
        path_form.addRow("Folder Desain:", design_dir_layout)
        
        # 3. Target Smart Object - Changed to text input
        self.smart_object_input = QLineEdit()
        self.smart_object_input.setPlaceholderText("Masukkan nama smart object yang akan diganti...")
        path_form.addRow("Target Smart Object:", self.smart_object_input)
        
        # 4. Output Directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Masukkan lokasi folder untuk hasil output...")
        output_dir_layout.addWidget(self.output_dir_input)
        
        self.output_dir_browse = QPushButton(browse_icon, "")
        self.output_dir_browse.setToolTip("Cari Folder Output")
        self.output_dir_browse.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(self.output_dir_browse)
        
        path_form.addRow("Folder Output:", output_dir_layout)
        
        # 5. Format Output
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPG"])
        self.format_combo.setToolTip("Pilih format file output")
        path_form.addRow("Format Output:", self.format_combo)
        
        path_group.setLayout(path_form)
        main_layout.addWidget(path_group)
        
        # Area untuk dua tabel berdampingan dengan splitter
        tables_splitter = QSplitter(Qt.Horizontal)
        
        # Wadah untuk tabel mockup dan labelnya
        mockup_container = QWidget()
        mockup_layout = QVBoxLayout(mockup_container)
        mockup_layout.setContentsMargins(0, 0, 0, 0)
        
        mockup_label = QLabel("Daftar File Mockup")
        mockup_label.setAlignment(Qt.AlignCenter)
        mockup_layout.addWidget(mockup_label)
        
        # Tabel untuk menampilkan daftar file PSD mockup
        self.file_table = QTableWidget(0, 4)
        self.file_table.setHorizontalHeaderLabels(["Nama File", "Ukuran (MB)", "Terakhir Diubah", "Lokasi Lengkap"])
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.file_table.setAlternatingRowColors(False)
        mockup_layout.addWidget(self.file_table)
        
        # Informasi total file mockup
        self.info_label = QLabel("0 file mockup ditemukan")
        mockup_layout.addWidget(self.info_label)
        
        # Wadah untuk tabel desain dan labelnya
        design_container = QWidget()
        design_layout = QVBoxLayout(design_container)
        design_layout.setContentsMargins(0, 0, 0, 0)
        
        design_label = QLabel("Daftar Desain untuk Smart Object")
        design_label.setAlignment(Qt.AlignCenter)
        design_layout.addWidget(design_label)
        
        # Tabel untuk menampilkan daftar file desain
        self.design_table = QTableWidget(0, 3)
        self.design_table.setHorizontalHeaderLabels(["Nama Desain", "Ukuran (MB)", "Terakhir Diubah"])
        self.design_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.design_table.setAlternatingRowColors(False)
        design_layout.addWidget(self.design_table)
        
        # Informasi total file desain
        self.design_info_label = QLabel("0 file desain ditemukan")
        design_layout.addWidget(self.design_info_label)
        
        # Tambahkan ke splitter
        tables_splitter.addWidget(mockup_container)
        tables_splitter.addWidget(design_container)
        tables_splitter.setSizes([600, 600])  # Ukuran awal yang sama
        
        main_layout.addWidget(tables_splitter)
        
        # Progress Bar
        progress_group = QGroupBox("Status Proses")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Siap untuk memproses")
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Tombol render mockup
        button_layout = QHBoxLayout()
        open_icon = qta.icon('fa6s.images', color='#2ecc71')
        self.open_button = QPushButton(open_icon, " Render Mockup")
        self.open_button.clicked.connect(self.open_path_in_photoshop)
        button_layout.addWidget(self.open_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Pilih Folder Sumber")
        if directory:
            self.path_input.setText(directory)
    
    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        if directory:
            self.output_dir_input.setText(directory)
    
    def browse_design_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Pilih Folder Desain")
        if directory:
            self.design_dir_input.setText(directory)
    
    def update_design_table(self):
        path = self.design_dir_input.text().strip()
        self.design_table.setRowCount(0)
        
        if not path or not os.path.exists(path):
            self.design_info_label.setText("0 file desain ditemukan")
            return
            
        try:
            design_files = []
            supported_formats = ['.psd', '.png', '.jpg', '.jpeg', '.tif', '.tiff']
            
            for file in os.listdir(path):
                file_lower = file.lower()
                if any(file_lower.endswith(ext) for ext in supported_formats):
                    file_path = os.path.join(path, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    mod_time = os.path.getmtime(file_path)
                    mod_time_str = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                    
                    design_files.append({
                        "name": file,
                        "size": file_size,
                        "modified": mod_time_str,
                        "path": file_path
                    })
            
            # Sort by name
            design_files.sort(key=lambda x: x["name"])
            
            # Add files to table
            self.design_table.setRowCount(len(design_files))
            for i, file_info in enumerate(design_files):
                self.design_table.setItem(i, 0, QTableWidgetItem(file_info["name"]))
                self.design_table.setItem(i, 1, QTableWidgetItem(f"{file_info['size']:.2f}"))
                self.design_table.setItem(i, 2, QTableWidgetItem(file_info["modified"]))
                
            self.design_info_label.setText(f"{len(design_files)} file desain ditemukan")
        except Exception as e:
            self.design_info_label.setText(f"Error: {str(e)}")
    
    def update_file_table(self):
        path = self.path_input.text().strip()
        self.file_table.setRowCount(0)
        
        if not path or not os.path.exists(path):
            self.info_label.setText("0 file mockup ditemukan")
            return
            
        try:
            psd_files = []
            for file in os.listdir(path):
                if file.lower().endswith(".psd"):
                    file_path = os.path.join(path, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
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
                
            self.info_label.setText(f"{len(psd_files)} file mockup ditemukan")
        except Exception as e:
            self.info_label.setText(f"Error: {str(e)}")
    
    def open_path_in_photoshop(self):
        path = self.path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "Peringatan", "Mohon masukkan lokasi folder mockup terlebih dahulu.")
            return
            
        if not os.path.exists(path):
            QMessageBox.warning(self, "Peringatan", "Folder mockup tidak valid atau tidak ditemukan.")
            return
            
        try:
            ps_exe = self.find_photoshop()
            if not ps_exe:
                QMessageBox.critical(self, "Error", "Photoshop tidak ditemukan.")
                return
                
            # Konversi path dengan forward slash untuk ExtendScript
            safe_path = path.replace("\\", "/")
            
            # Dapatkan format output yang dipilih
            output_format = self.format_combo.currentText().lower()
            
            # Pastikan direktori script ada
            script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script")
            os.makedirs(script_dir, exist_ok=True)
            
            # Buat script JSX untuk membuka path
            jsx_path = os.path.join(script_dir, "open_psd.jsx")
            jsx_code = f'''
// Script untuk membuka file PSD di Photoshop
var path = new Folder("{safe_path}");
var files = path.getFiles("*.psd");
var outputFormat = "{output_format}";

if (files.length > 0) {{
    for (var i = 0; i < files.length; i++) {{
        app.open(files[i]);
    }}
    alert("Berhasil membuka " + files.length + " file PSD dari folder " + path + "\\nFormat output: " + outputFormat.toUpperCase());
}} else {{
    alert("Tidak ditemukan file PSD di folder " + path);
}}
'''
            
            with open(jsx_path, "w", encoding="utf-8") as f:
                f.write(jsx_code)
                
            # Simulasi progress untuk demo (tanpa fungsi nyata)
            self.progress_label.setText("Memulai proses render...")
            self.progress_bar.setValue(5)
            QApplication.processEvents()
            
            # Jalankan Photoshop tanpa menunggu output
            subprocess.Popen([ps_exe, "-r", jsx_path], 
                           shell=True, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Reset progress status setelah selesai
            self.progress_bar.setValue(0)
            self.progress_label.setText("Siap untuk memproses")
            
            # Tampilkan sukses tanpa memperhatikan exit code
            QMessageBox.information(self, "Sukses", f"Perintah render mockup berhasil dikirim ke Photoshop.\nFormat output: {output_format.upper()}")
            
        except Exception as e:
            self.progress_label.setText("Error dalam proses")
            QMessageBox.critical(self, "Error", f"Gagal menjalankan Photoshop:\n{str(e)}")

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
