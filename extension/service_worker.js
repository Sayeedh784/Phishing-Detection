const apiURL = "http://127.0.0.1:8000/api/predict/";

// ✅ Create context menu items once installed
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "scan_selected_as_email",
    title: "Scan Selected Text as Email",
    contexts: ["selection"]
  });

  chrome.contextMenus.create({
    id: "scan_selected_as_url",
    title: "Scan Selected Text as URL",
    contexts: ["selection"]
  });
});

// ✅ When user clicks menu
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const text = (info.selectionText || "").trim();
  if (!text) return;

  const scanType =
    info.menuItemId === "scan_selected_as_url" ? "url" : "email";

  try {
    const res = await fetch(apiURL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: scanType, text })
    });

    const data = await res.json();

    chrome.runtime.sendMessage({
      type: "SELECT_TEXT_SCAN_RESULT",
      data: data
    });

  } catch (err) {
    chrome.runtime.sendMessage({
      type: "SELECT_TEXT_SCAN_RESULT",
      data: {
        error: "API connection failed",
        details: err.message
      }
    });
  }
});
