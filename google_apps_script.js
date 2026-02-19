/**
 * Halal Store Registration — Google Apps Script (Webhook)
 *
 * Setup:
 *   1. Create a Google Spreadsheet
 *   2. Extensions > Apps Script
 *   3. Paste this code and save
 *   4. Run setupSheet() once to create headers
 *   5. Deploy > New deployment > Web app
 *      - Execute as: Me
 *      - Who has access: Anyone
 *   6. Copy the Web app URL into the Streamlit sidebar
 */

function doPost(e) {
  try {
    var payload = JSON.parse(e.postData.contents);
    var data = payload.json_data;
    var timestamp = new Date();

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Submissions")
                || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

    // --- Save images to Drive ---
    var ssFile = DriveApp.getFileById(SpreadsheetApp.getActiveSpreadsheet().getId());
    var parentFolder = ssFile.getParents().next();

    var submissionsFolder;
    var folders = parentFolder.getFoldersByName("store_submissions");
    if (folders.hasNext()) {
      submissionsFolder = folders.next();
    } else {
      submissionsFolder = parentFolder.createFolder("store_submissions");
    }

    var folderName = Utilities.formatDate(timestamp, "Asia/Tokyo", "yyyyMMdd_HHmmss")
                     + "_" + (data.store_name || "store");
    var storeFolder = submissionsFolder.createFolder(folderName);

    // Save data.json
    storeFolder.createFile(
      "data.json",
      JSON.stringify(data, null, 2),
      "application/json"
    );

    // Save images
    var imageFolder = storeFolder.createFolder("images");
    var imageCount = 0;
    if (payload.images && payload.images.length > 0) {
      for (var i = 0; i < payload.images.length; i++) {
        var img = payload.images[i];
        try {
          var decoded = Utilities.base64Decode(img.data);
          var blob = Utilities.newBlob(decoded, "image/webp", img.filename);
          imageFolder.createFile(blob);
          imageCount++;
        } catch (imgErr) {
          Logger.log("Image save error: " + img.filename + " - " + imgErr);
        }
      }
    }

    // --- Append row to sheet ---
    var commitmentTitles = (data.commitments || []).map(function(c) {
      return c.title;
    }).join(" / ");

    var menuNames = (data.menus || []).map(function(m) {
      return m.name;
    }).join(" / ");

    var row = [
      timestamp,
      data.store_name || "",
      data.phone || "",
      data.contact_name || "",
      data.email || "",
      data.business_hours || "",
      data.regular_holiday || "",
      data.nearest_station || "",
      (data.languages || []).join(", "),
      data.wifi ? "Yes" : "No",
      (data.payment_methods || []).join(", "),
      data.halal_level || "",
      data.preparation_transparency || "",
      commitmentTitles,
      menuNames,
      imageCount,
      storeFolder.getUrl(),
    ];

    sheet.appendRow(row);

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      folder_url: storeFolder.getUrl(),
      image_count: imageCount
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    Logger.log("doPost error: " + error);
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: "ok",
    message: "Halal Store Registration API is running."
  })).setMimeType(ContentService.MimeType.JSON);
}

/** Run once to set up the header row. */
function setupSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Submissions");
  if (!sheet) {
    sheet = ss.insertSheet("Submissions");
  }
  var headers = [
    "Timestamp",
    "Store Name",
    "Phone",
    "Contact Name",
    "Email",
    "Business Hours",
    "Regular Holiday",
    "Nearest Station",
    "Languages",
    "Wi-Fi",
    "Payment Methods",
    "Halal Level",
    "Preparation Transparency",
    "Highlights",
    "Menus",
    "Image Count",
    "Drive Folder",
  ];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight("bold");
  sheet.setFrozenRows(1);

  // Auto-resize columns
  for (var i = 1; i <= headers.length; i++) {
    sheet.autoResizeColumn(i);
  }
}
