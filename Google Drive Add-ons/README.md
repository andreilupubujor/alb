# Google Docs Comment Exporter

This Google Apps Script automates the process of extracting comments and nested replies from a Google Doc and organizes them into a Google Sheet. It captures context, comment content, author names, and timestamps.

## Features
* Extracts top-level comments and nested replies.
* Captures "Context" (the text the comment was made on).
* Includes timestamps and author names.
* Handles large documents using API pagination (nextPageToken).

## Setup Instructions

### 1. Prepare the Google Sheet
* Create a new Google Sheet.
* Rename the first tab to `Comments`.
* Copy the **Spreadsheet ID** from the URL (the string between `/d/` and `/edit`).

### 2. Prepare the Google Doc
* Open the Doc you want to export from.
* Copy the **Document ID** from the URL.

### 3. Configure the Script
1. In your Google Sheet, go to **Extensions > Apps Script**.
2. Paste the code from `Code.gs` in this repository into the editor.
3. Replace the `docId` and `ssId` placeholders with your actual IDs.
4. On the left sidebar, click the **+** next to **Services**.
5. Select **Drive API** and click **Add**.

### 4. Run the Script
1. Select the function `listAllCommentsAndReplies` from the toolbar.
2. Click **Run**.
3. Grant the necessary permissions when prompted (Review Permissions > Advanced > Go to... > Allow).
