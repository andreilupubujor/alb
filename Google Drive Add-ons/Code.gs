/**
 * Extracts all comments and replies from a Google Doc to a Google Sheet.
 * Requires: Drive API Service (v3)
 */
function listAllCommentsAndReplies() {
  // Replace these placeholders with your actual IDs
  var docId = 'PASTE_YOUR_GOOGLE_DOC_ID_HERE'; 
  var ssId = 'PASTE_YOUR_SPREADSHEET_ID_HERE';
  
  var rows = [];
  var pageToken = null;

  // Header Row
  rows.push(["Context/Type", "Comment Content", "Author", "Date/Time"]);

  try {
    do {
      var response = Drive.Comments.list(docId, {
        fields: 'nextPageToken, comments(content,author,createdTime,quotedFileContent,replies(content,author,createdTime))',
        pageSize: 100,
        pageToken: pageToken
      });

      if (response.comments) {
        response.comments.forEach(function(c) {
          // Add Main Comment
          rows.push([
            c.quotedFileContent ? "Context: " + c.quotedFileContent.value : "Main Comment",
            c.content,
            c.author ? c.author.displayName : 'Anonymous',
            new Date(c.createdTime).toLocaleString()
          ]);

          // Add Nested Replies
          if (c.replies && c.replies.length > 0) {
            c.replies.forEach(function(r) {
              rows.push([
                "   ↳ Reply",
                r.content,
                r.author ? r.author.displayName : 'Anonymous',
                new Date(r.createdTime).toLocaleString()
              ]);
            });
          }
        });
      }
      pageToken = response.nextPageToken;
    } while (pageToken);

    var ss = SpreadsheetApp.openById(ssId);
    var sheet = ss.getSheetByName('Comments');
    
    if (sheet && rows.length > 0) {
      sheet.clear();
      sheet.getRange(1, 1, rows.length, 4).setValues(rows);
      sheet.getRange(1, 1, 1, 4).setFontWeight("bold");
      Logger.log('Success!');
    }
  } catch (e) {
    Logger.log('Error: ' + e.toString());
  }
}
