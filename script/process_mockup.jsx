
#target photoshop

// Configuration
var psdPath = "";
var designPath = "";
var smartObjectName = "";
var outputPath = "";
var outputFormat = "png";
var statusFile = "";
var firstDesign = false;
var lastDesign = false;

// Simplified status writing without using JSON
function writeStatus(status, message) {
    var file = new File(statusFile);
    file.open("w");
    file.write(status + ": " + message);
    file.close();
}

function main() {
    try {
        writeStatus("running", "Processing");
        
        // If this is the first design, open the PSD first
        var doc;
        if (firstDesign) {
            app.open(new File(psdPath));
            doc = app.activeDocument;
        } else {
            doc = app.activeDocument;
        }
        
        // Find the smart object layer by name
        var targetLayer = null;
        for (var i = 0; i < doc.layers.length; i++) {
            if (doc.layers[i].name == smartObjectName) {
                targetLayer = doc.layers[i];
                break;
            }
        }
        
        if (!targetLayer) {
            writeStatus("error", "Smart object not found: " + smartObjectName);
            return;
        }
        
        // Select the layer and edit the smart object
        doc.activeLayer = targetLayer;
        
        // Open the smart object using Edit Contents
        var idPlcL = stringIDToTypeID("placedLayerEditContents");
        executeAction(idPlcL, undefined, DialogModes.NO);
        
        // We're now inside the smart object
        var smartObjectDoc = app.activeDocument;
        
        // Remember smart object dimensions
        var soWidth = smartObjectDoc.width;
        var soHeight = smartObjectDoc.height;
        
        // Open design file
        var designDoc = app.open(new File(designPath));
        
        // Copy content from design file
        designDoc.selection.selectAll();
        designDoc.selection.copy();
        designDoc.close(SaveOptions.DONOTSAVECHANGES);
        
        // Place new design as a new layer on top (without trying to clear content)
        smartObjectDoc.paste();
        
        // Get the pasted layer (should be the top layer)
        var pastedLayer = smartObjectDoc.activeLayer;
        
        // Fit the design proportionally
        fitLayerProportionally(pastedLayer, soWidth, soHeight);
        
        // Save and close the smart object
        smartObjectDoc.save();
        smartObjectDoc.close(SaveOptions.DONOTSAVECHANGES);
        
        // Export the document to the specified format
        exportDocument(doc, outputPath, outputFormat);
        
        // If this is the last design for this PSD, close the document without saving
        if (lastDesign) {
            doc.close(SaveOptions.DONOTSAVECHANGES);
        }
        
        writeStatus("complete", "Done");
    } catch (e) {
        writeStatus("error", e.toString());
    }
}

// Function to fit layer proportionally to target dimensions
function fitLayerProportionally(layer, targetWidth, targetHeight) {
    try {
        // Make sure the layer is selected
        app.activeDocument.activeLayer = layer;
        
        // Get current dimensions
        var bounds = layer.bounds;
        var layerWidth = bounds[2] - bounds[0];
        var layerHeight = bounds[3] - bounds[1];
        
        // Calculate scaling factors
        var widthRatio = targetWidth / layerWidth;
        var heightRatio = targetHeight / layerHeight;
        
        // Use the larger scaling factor to ensure the image covers the smart object
        // This will maintain aspect ratio while ensuring one dimension fits exactly
        var scaleFactor = Math.max(widthRatio, heightRatio) * 100;
        
        // Resize the layer
        layer.resize(scaleFactor, scaleFactor, AnchorPosition.MIDDLECENTER);
        
        // Center the layer
        centerLayer(layer);
    } catch (e) {
        // Silent error handling
    }
}

// Function to center a layer in the document
function centerLayer(layer) {
    var doc = app.activeDocument;
    var bounds = layer.bounds;
    var layerWidth = bounds[2] - bounds[0];
    var layerHeight = bounds[3] - bounds[1];
    
    var docWidth = doc.width.value;
    var docHeight = doc.height.value;
    
    var deltaX = (docWidth - layerWidth) / 2;
    var deltaY = (docHeight - layerHeight) / 2;
    
    // Adjust for current position
    deltaX = deltaX - bounds[0];
    deltaY = deltaY - bounds[1];
    
    // Move the layer
    layer.translate(deltaX, deltaY);
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
