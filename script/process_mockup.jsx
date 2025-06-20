// This file is a template and will be overwritten dynamically by the application
// when processing mockups with a specific PSD and design.

#target photoshop

// Configuration - will be filled dynamically by the Python app
var psdPath = "";
var designPath = "";
var smartObjectName = "";
var outputPath = "";
var outputFormat = "png";
var statusFile = "";
var firstDesign = true;
var lastDesign = false;

// Function to write status updates without using JSON (fixed)
function writeStatus(status, message) {
    var file = new File(statusFile);
    file.encoding = "UTF-8";
    file.open("w");
    file.write('{"status":"' + status + '","message":"' + message + '"}');
    file.close();
}

function main() {
    try {
        writeStatus("running", "Membuka file PSD");
        
        // If this is the first design, open the PSD first
        var doc;
        if (firstDesign) {
            app.open(new File(psdPath));
            doc = app.activeDocument;
        } else {
            doc = app.activeDocument;
        }
        
        writeStatus("running", "Mencari smart object");
        
        // Find the smart object layer by name
        var targetLayer = null;
        for (var i = 0; i < doc.layers.length; i++) {
            if (doc.layers[i].name == smartObjectName) {
                targetLayer = doc.layers[i];
                break;
            }
        }
        
        if (!targetLayer) {
            writeStatus("error", "Smart object dengan nama '" + smartObjectName + "' tidak ditemukan");
            return;
        }
        
        writeStatus("running", "Membuka dan mengganti konten smart object");
        
        // Select the layer and edit the smart object
        doc.activeLayer = targetLayer;
        
        // Open smart object using placedLayerEditContents (more reliable)
        var idPlcL = stringIDToTypeID("placedLayerEditContents");
        executeAction(idPlcL, undefined, DialogModes.NO);
        
        // We're now inside the smart object
        var smartObjectDoc = app.activeDocument;
        
        // Open the design file
        var designDoc = app.open(new File(designPath));
        
        // Copy content from design file
        designDoc.selection.selectAll();
        designDoc.selection.copy();
        designDoc.close(SaveOptions.DONOTSAVECHANGES);
        
        // Paste into smart object
        smartObjectDoc.paste();
        
        // Fit layer to document dimensions if needed
        if (smartObjectDoc.layers.length > 0) {
            smartObjectDoc.activeLayer = smartObjectDoc.layers[0];
            fitLayerToCanvas(smartObjectDoc.activeLayer);
        }
        
        writeStatus("running", "Menyimpan perubahan smart object");
        
        // Save and close the smart object
        smartObjectDoc.save();
        smartObjectDoc.close(SaveOptions.DONOTSAVECHANGES);
        
        writeStatus("running", "Mengeksport ke " + outputFormat.toUpperCase());
        
        // Export the document to the specified format
        exportDocument(doc, outputPath, outputFormat);
        
        // If this is the last design for this PSD, close the document without saving
        if (lastDesign) {
            doc.close(SaveOptions.DONOTSAVECHANGES);
        }
        
        writeStatus("complete", "Rendering selesai");
    } catch (e) {
        writeStatus("error", "Error: " + e.toString());
    }
}

// Helper function to fit layer to canvas
function fitLayerToCanvas(layer) {
    try {
        var docWidth = app.activeDocument.width.value;
        var docHeight = app.activeDocument.height.value;
        
        app.activeDocument.activeLayer = layer;
        app.activeDocument.activeLayer.resize(100, 100, AnchorPosition.MIDDLECENTER);
    } catch (e) {
        // Silent error handling
    }
}

function exportDocument(doc, outputPath, format) {
    var saveFile = new File(outputPath);
    var saveOptions;
    
    if (format === 'jpg') {
        saveOptions = new JPEGSaveOptions();
        saveOptions.embedColorProfile = true;
        saveOptions.formatOptions = FormatOptions.STANDARDBASELINE;
        saveOptions.matte = MatteType.NONE;
        saveOptions.quality = 12; // Maximum quality
    } else {
        // Default to PNG
        saveOptions = new PNGSaveOptions();
        saveOptions.compression = 0; // No compression
        saveOptions.interlaced = false;
    }
    
    doc.saveAs(saveFile, saveOptions, true, Extension.LOWERCASE);
}

// Run the script
main();
        saveOptions.compression = 0; // No compression
        saveOptions.interlaced = false;
    }
    
    doc.saveAs(saveFile, saveOptions, true, Extension.LOWERCASE);
}

// Run the script
main();
