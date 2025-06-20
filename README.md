# Mockup-Renderer

An advanced PySide6 application for batch rendering PSD mockups by replacing smart objects with design files and exporting to various formats.

## Features

- Browse and select directories containing PSD mockup files
- Select a folder of design files to apply to each mockup
- Replace smart objects in each mockup with each design
- Export to PNG or JPG format automatically
- Visual progress tracking with detailed status updates
- Always-on-top window for easy monitoring
- Supports batching (render each mockup with each design)
- Organized output structure with numbered files in PSD-named folders

## Requirements

- Python 3.8+
- PySide6
- qtawesome
- Adobe Photoshop (any recent version)

## Usage

1. Run `Launcher.bat` or execute `python main.py`
2. Set folder paths:
   - Source Directory: Folder containing mockup PSD files
   - Design Directory: Folder containing design files to apply
   - Target Smart Object: Name of smart object layer to replace in mockups
   - Output Directory: Folder for saving exported images
3. Select output format (PNG or JPG)
4. Click "Render Mockup" to begin the batch process

## Output Structure

The program creates a well-organized output structure: