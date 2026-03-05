// content.js
// Runs automatically on every http/https webpage
// Sends current page URL to popup when popup requests it

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "GET_CURRENT_URL") {
    sendResponse({ url: window.location.href });
  }
});
