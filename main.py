import sys
import subprocess
import os
import time
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QMessageBox, QLabel, 
                             QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox, QFormLayout, QProgressBar, QSplitter, QComboBox)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QColor
import qtawesome as qta
import datetime
import json
import tempfile

class MockupRenderer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mockup Renderer")
        self.resize(1200, 650)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        
        self.processing = False
        self.current_psd_index = -1
        self.current_design_index = -1
        self.psd_files = []
        self.design_files = []
        
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
        self.progress_bar.setFormat("%v% - %p%")
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Siap untuk memproses")
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Tombol render mockup
        button_layout = QHBoxLayout()
        open_icon = qta.icon('fa6s.images', color='#2ecc71')
        self.render_button = QPushButton(open_icon, " Render Mockup")
        self.render_button.clicked.connect(self.start_rendering)
        button_layout.addWidget(self.render_button)
        
        # Tombol cancel
        cancel_icon = qta.icon('fa6s.xmark', color='#e74c3c')
        self.cancel_button = QPushButton(cancel_icon, " Batal")
        self.cancel_button.clicked.connect(self.cancel_rendering)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Timer untuk proses rendering
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.process_rendering)
        
        # Timer untuk polling status
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_process_status)
        self.status_timer.setInterval(500)  # Check every 0.5 second
        
        # Tracking number per PSD
        self.output_counters = {}
        
        # Warna highlight kuning transparan
        self.highlight_color = QColor(255, 255, 0, 13)  # RGBA with 0.05 alpha
        
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
            self.design_files = design_files
            
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
            self.psd_files = psd_files
            
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
    
    def validate_inputs(self):
        mockup_dir = self.path_input.text().strip()
        if not mockup_dir or not os.path.exists(mockup_dir):
            QMessageBox.warning(self, "Peringatan", "Folder sumber mockup tidak ditemukan.")
            return False
            
        if not self.psd_files:
            QMessageBox.warning(self, "Peringatan", "Tidak ada file mockup (.psd) ditemukan di folder sumber.")
            return False
        
        design_dir = self.design_dir_input.text().strip()
        if not design_dir or not os.path.exists(design_dir):
            QMessageBox.warning(self, "Peringatan", "Folder desain tidak ditemukan.")
            return False
            
        if not self.design_files:
            QMessageBox.warning(self, "Peringatan", "Tidak ada file desain ditemukan di folder desain.")
            return False
            
        smart_object_name = self.smart_object_input.text().strip()
        if not smart_object_name:
            QMessageBox.warning(self, "Peringatan", "Nama smart object tidak boleh kosong.")
            return False
            
        output_dir = self.output_dir_input.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "Peringatan", "Folder output belum ditentukan.")
            return False
            
        # Pastikan folder output ada, buat jika belum ada
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Gagal membuat folder output: {str(e)}")
                return False
                
        return True
    
    def start_rendering(self):
        if self.processing:
            return
            
        if not self.validate_inputs():
            return
            
        self.processing = True
        self.render_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        
        # Reset indices
        self.current_psd_index = -1
        self.current_design_index = -1
        
        # Reset output counters
        self.output_counters = {}
        
        # Calculate total operations for progress bar
        total_psd_files = len(self.psd_files)
        total_design_files = len(self.design_files)
        total_operations = total_psd_files * total_design_files
        self.total_operations = total_operations
        self.completed_operations = 0
        
        # Update progress
        self.update_progress(0, "Memulai proses rendering...")
        
        # Start rendering process
        self.render_timer.start(100)  # Start with a small delay
    
    def cancel_rendering(self):
        if not self.processing:
            return
            
        self.processing = False
        self.render_timer.stop()
        self.status_timer.stop()
        
        # Kill any active Photoshop script
        self.terminate_photoshop_script()
        
        # Reset UI
        self.render_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Proses dibatalkan")
        
        # Reset row highlights
        self.reset_table_highlights()
    
    def reset_table_highlights(self):
        # Reset tables by removing all background colors
        for row in range(self.file_table.rowCount()):
            for col in range(self.file_table.columnCount()):
                item = self.file_table.item(row, col)
                if item:
                    item.setBackground(QColor(0, 0, 0, 0))  # Transparent background
        
        for row in range(self.design_table.rowCount()):
            for col in range(self.design_table.columnCount()):
                item = self.design_table.item(row, col)
                if item:
                    item.setBackground(QColor(0, 0, 0, 0))  # Transparent background
    
    def highlight_current_files(self):
        # Reset previous highlights
        self.reset_table_highlights()
        
        # Highlight current PSD file with subtle yellow
        if self.current_psd_index >= 0 and self.current_psd_index < len(self.psd_files):
            for col in range(self.file_table.columnCount()):
                item = self.file_table.item(self.current_psd_index, col)
                if item:
                    item.setBackground(self.highlight_color)
        
        # Highlight current design file with subtle yellow
        if self.current_design_index >= 0 and self.current_design_index < len(self.design_files):
            for col in range(self.design_table.columnCount()):
                item = self.design_table.item(self.current_design_index, col)
                if item:
                    item.setBackground(self.highlight_color)
    
    def process_rendering(self):
        if not self.processing:
            return
            
        self.render_timer.stop()
        
        # Move to next PSD or design file
        if self.current_design_index < 0 or self.current_design_index >= len(self.design_files) - 1:
            # Move to next PSD file
            self.current_psd_index += 1
            self.current_design_index = 0
            
            if self.current_psd_index >= len(self.psd_files):
                # All files processed
                self.rendering_complete()
                return
        else:
            # Move to next design file for the same PSD
            self.current_design_index += 1
        
        # Update UI highlights
        self.highlight_current_files()
        
        # Get current files
        psd_file = self.psd_files[self.current_psd_index]
        design_file = self.design_files[self.current_design_index]
        
        # Check if this is the first design for this PSD
        first_design = (self.current_design_index == 0)
        # Check if this is the last design for this PSD
        last_design = (self.current_design_index == len(self.design_files) - 1)
        
        # Calculate progress
        self.completed_operations += 1
        progress = int((self.completed_operations / self.total_operations) * 100)
        
        # Create and run JSX script for processing current files
        self.run_photoshop_script(psd_file, design_file, first_design, last_design)
        
        # Update progress with current operation
        status_msg = f"Memproses: {psd_file['name']} dengan desain: {design_file['name']}..."
        self.update_progress(progress, status_msg)
        
        # Start polling for completion
        self.status_timer.start()
    
    def run_photoshop_script(self, psd_file, design_file, first_design, last_design):
        try:
            ps_exe = self.find_photoshop()
            if not ps_exe:
                raise Exception("Photoshop tidak ditemukan.")
            
            # Get configuration data
            source_path = self.path_input.text().strip()
            design_path = self.design_dir_input.text().strip()
            output_path = self.output_dir_input.text().strip()
            smart_object_name = self.smart_object_input.text().strip()
            output_format = self.format_combo.currentText().lower()
            
            # Create status file to monitor progress
            status_file = os.path.join(tempfile.gettempdir(), "mockup_render_status.json")
            
            # Reset status
            with open(status_file, "w", encoding="utf-8") as f:
                f.write('{"status":"running","message":"Starting process"}')
            
            # Build script path
            script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script")
            os.makedirs(script_dir, exist_ok=True)
            jsx_path = os.path.join(script_dir, "process_mockup.jsx")
            
            # Convert paths for JSX
            psd_path = psd_file["path"].replace("\\", "/")
            design_path = design_file["path"].replace("\\", "/")
            output_path = output_path.replace("\\", "/")
            status_file = status_file.replace("\\", "/")
            
            # Generate folder name from PSD file name
            psd_name = os.path.splitext(os.path.basename(psd_file["path"]))[0]
            
            # Create output subfolder based on PSD name
            psd_output_dir = os.path.join(output_path, psd_name)
            os.makedirs(psd_output_dir, exist_ok=True)
            psd_output_dir = psd_output_dir.replace("\\", "/")
            
            # Get or initialize counter for this PSD file
            if psd_name not in self.output_counters:
                self.output_counters[psd_name] = 1
            else:
                if first_design:  # Reset counter when starting a new PSD
                    self.output_counters[psd_name] = 1
                
            # Generate numbered output filename
            current_number = self.output_counters[psd_name]
            output_filename = f"{psd_name}_{current_number}.{output_format}"
            output_file_path = os.path.join(psd_output_dir, output_filename).replace("\\", "/")
            
            # Increment the counter for the next file
            self.output_counters[psd_name] += 1
            
            # Create the JSX script content with updated approach that doesn't use JSON
            jsx_code = f'''
#target photoshop

// Configuration
var psdPath = "{psd_path}";
var designPath = "{design_path}";
var smartObjectName = "{smart_object_name}";
var outputPath = "{output_file_path}";
var outputFormat = "{output_format}";
var statusFile = "{status_file}";
var firstDesign = {str(first_design).lower()};
var lastDesign = {str(last_design).lower()};

// Function to write status updates without using JSON
function writeStatus(status, message) {{
    var file = new File(statusFile);
    file.encoding = "UTF-8";
    file.open("w");
    file.write('{{"status":"' + status + '","message":"' + message + '"}}');
    file.close();
}}

function main() {{
    try {{
        writeStatus("running", "Membuka file PSD");
        
        // If this is the first design, open the PSD first
        var doc;
        if (firstDesign) {{
            app.open(new File(psdPath));
            doc = app.activeDocument;
        }} else {{
            doc = app.activeDocument;
        }}
        
        writeStatus("running", "Mencari smart object");
        
        // Find the smart object layer by name
        var targetLayer = null;
        for (var i = 0; i < doc.layers.length; i++) {{
            if (doc.layers[i].name == smartObjectName) {{
                targetLayer = doc.layers[i];
                break;
            }}
        }}
        
        if (!targetLayer) {{
            writeStatus("error", "Smart object dengan nama '" + smartObjectName + "' tidak ditemukan");
            return;
        }}
        
        writeStatus("running", "Membuka dan mengganti konten smart object");
        
        // Select the layer and edit the smart object
        doc.activeLayer = targetLayer;
        
        // Open smart object using placedLayerEditContents
        var idPlcL = stringIDToTypeID("placedLayerEditContents");
        executeAction(idPlcL, undefined, DialogModes.NO);
        
        // We're now inside the smart object
        var smartObjectDoc = app.activeDocument;
        
        // Open design file
        var designDoc = app.open(new File(designPath));
        
        // Copy content from design file
        designDoc.selection.selectAll();
        designDoc.selection.copy();
        designDoc.close(SaveOptions.DONOTSAVECHANGES);
        
        // Paste into smart object
        smartObjectDoc.paste();
        
        // Fit layer to document dimensions if needed
        if (smartObjectDoc.layers.length > 0) {{
            smartObjectDoc.activeLayer = smartObjectDoc.layers[0];
            
            // Resize placed design to fit the document
            smartObjectDoc.activeLayer.resize(100, 100, AnchorPosition.MIDDLECENTER);
        }}
        
        writeStatus("running", "Menyimpan perubahan smart object");
        
        // Save and close the smart object
        smartObjectDoc.save();
        smartObjectDoc.close(SaveOptions.DONOTSAVECHANGES);
        
        writeStatus("running", "Mengeksport ke " + outputFormat.toUpperCase());
        
        // Export the document to the specified format
        exportDocument(doc, outputPath, outputFormat);
        
        // If this is the last design for this PSD, close the document without saving
        if (lastDesign) {{
            doc.close(SaveOptions.DONOTSAVECHANGES);
        }}
        
        writeStatus("complete", "Rendering selesai");
    }} catch (e) {{
        writeStatus("error", "Error: " + e.toString());
    }}
}}

function exportDocument(doc, outputPath, format) {{
    var saveFile = new File(outputPath);
    var saveOptions;
    
    if (format === 'jpg') {{
        saveOptions = new JPEGSaveOptions();
        saveOptions.embedColorProfile = true;
        saveOptions.formatOptions = FormatOptions.STANDARDBASELINE;
        saveOptions.matte = MatteType.NONE;
        saveOptions.quality = 12; // Maximum quality
    }} else {{
        // Default to PNG
        saveOptions = new PNGSaveOptions();
        saveOptions.compression = 0; // No compression
        saveOptions.interlaced = false;
    }}
    
    doc.saveAs(saveFile, saveOptions, true, Extension.LOWERCASE);
}}

// Run the script
main();
'''
            
            # Write script to file
            with open(jsx_path, "w", encoding="utf-8") as f:
                f.write(jsx_code)
            
            # Run the script in Photoshop
            self.ps_process = subprocess.Popen(
                [ps_exe, "-r", jsx_path],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.status_file = status_file
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menjalankan proses: {str(e)}")
            self.cancel_rendering()
    
    def check_process_status(self):
        if not self.processing:
            return
            
        try:
            # Check if status file exists
            if not os.path.exists(self.status_file):
                return
                
            # Read status file
            with open(self.status_file, "r", encoding="utf-8") as f:
                status_text = f.read()
            
            # Parse JSON manually if needed
            try:
                status_data = json.loads(status_text)
                status = status_data.get("status", "")
                message = status_data.get("message", "")
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                if "complete" in status_text:
                    status = "complete"
                    message = "Rendering selesai"
                elif "error" in status_text:
                    status = "error"
                    message = "Error dalam proses"
                else:
                    status = "running"
                    message = "Proses berjalan"
            
            if status == "error":
                # Error occurred
                QMessageBox.critical(self, "Error", f"Error dalam proses: {message}")
                self.cancel_rendering()
                return
                
            if status == "complete":
                # Current operation completed, move to next
                self.status_timer.stop()
                self.render_timer.start(500)  # Start next operation with delay
                return
                
            # Update progress message with current status
            self.progress_label.setText(message)
            
        except Exception as e:
            # Error reading status
            print(f"Error checking status: {str(e)}")
    
    def rendering_complete(self):
        self.processing = False
        self.status_timer.stop()
        
        # Reset UI
        self.render_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        # Update progress
        self.update_progress(100, "Rendering selesai!")
        
        # Reset row highlights
        self.reset_table_highlights()
        
        # Show completion message
        QMessageBox.information(
            self, 
            "Sukses", 
            f"Proses rendering selesai!\n\n"
            f"Total mockup: {len(self.psd_files)}\n"
            f"Total desain: {len(self.design_files)}\n"
            f"Total file output: {self.total_operations}"
        )
    
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        # Format the progress bar text
        self.progress_bar.setFormat(f"{value}% - {message}")
        QApplication.processEvents()
    
    def terminate_photoshop_script(self):
        if hasattr(self, 'ps_process') and self.ps_process:
            try:
                self.ps_process.terminate()
            except:
                pass

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
    
    def closeEvent(self, event):
        # Stop timers and processes on window close
        if self.processing:
            self.cancel_rendering()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set aplikasi style
    app.setStyle("Fusion")
    
    window = MockupRenderer()
    window.show()
    sys.exit(app.exec())
