document.addEventListener("DOMContentLoaded", () => {
  const urlInput = document.getElementById("urlInput");
  const emailInput = document.getElementById("emailInput");
  const scanTypeSelector = document.getElementById("scanTypeSelector");
  const urlSection = document.getElementById("urlSection");
  const emailSection = document.getElementById("emailSection");
  const resultBox = document.getElementById("resultBox");
  const resultBadge = document.getElementById("resultBadge");
  const confidenceBar = document.getElementById("confidenceBar");
  const finalScore = document.getElementById("finalScore");
  const trustedDomain = document.getElementById("trustedDomain");
  const ruleFlags = document.getElementById("ruleFlags");
  const riskLevel = document.getElementById("riskLevel");
  const actionAdvice = document.getElementById("actionAdvice");
  const scanTimestamp = document.getElementById("scanTimestamp");

  // Dropdown Logic
  scanTypeSelector.addEventListener("change", () => {
    resultBox.style.display = "none";
    if (scanTypeSelector.value === "url") {
      urlSection.style.display = "block";
      emailSection.style.display = "none";
    } else {
      urlSection.style.display = "none";
      emailSection.style.display = "block";
    }
  });

  // Auto-fill URL
  chrome.tabs?.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs?.[0]?.url) urlInput.value = tabs[0].url;
  });

  async function scan(type) {
    const text = type === "url" ? urlInput.value.trim() : emailInput.value.trim();
    if (!text) return alert("Please enter content to scan.");

    resultBox.style.display = "block";
    resultBadge.textContent = "SCANNING...";
    resultBadge.className = "result-badge badge-scan";

    try {
      const response = await fetch("http://127.0.0.1:8000/api/predict/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type, text }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Server Error");

      renderResult(data);
    } catch (err) {
      resultBadge.textContent = "ERROR";
      resultBadge.className = "result-badge badge-phish";
      riskLevel.textContent = "Connection Failed";
      actionAdvice.textContent = "Ensure Django is running on Port 8000.";
    }
  }

  function renderResult(data) {
    const isPhish = data.label?.toLowerCase() === "phishing";
    const score = data.score || 0;

    resultBadge.textContent = isPhish ? "PHISHING" : "LEGITIMATE";
    resultBadge.className = `result-badge ${isPhish ? 'badge-phish' : 'badge-legit'}`;
    
    confidenceBar.style.width = `${(score * 100)}%`;
    finalScore.textContent = score.toFixed(4);
    
    const explanation = data.explanation || {};
    trustedDomain.textContent = explanation.trusted_domain ? "YES ✅" : "NO ❌";
    scanTimestamp.textContent = new Date().toLocaleTimeString();

    // Risk Analysis Text
    if (score < 0.15) {
      riskLevel.textContent = "Safe: High Trust";
      riskLevel.style.color = "#00ffd1";
      actionAdvice.textContent = "This site matches safe community patterns.";
    } else if (score < 0.6) {
      riskLevel.textContent = "Caution: Unknown Pattern";
      riskLevel.style.color = "#ffb000";
      actionAdvice.textContent = "Avoid entering passwords on this site.";
    } else {
      riskLevel.textContent = "Danger: Likely Phishing";
      riskLevel.style.color = "#ff3b3b";
      actionAdvice.textContent = "Close this tab immediately to stay safe.";
    }

    ruleFlags.innerHTML = "";
    (explanation.rule_based_flags || []).forEach(f => {
      const span = document.createElement("span");
      span.className = "chip-warn";
      span.textContent = f;
      ruleFlags.appendChild(span);
    });
  }

  document.getElementById("scanUrlBtn").onclick = () => scan("url");
  document.getElementById("scanEmailBtn").onclick = () => scan("email");
});