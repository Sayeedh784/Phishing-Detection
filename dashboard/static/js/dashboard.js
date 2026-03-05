const resultArea = document.getElementById("resultArea");

function escapeHTML(str) {
  return str.replace(/[&<>"']/g, (m) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  }[m]));
}

function getRiskLevel(score) {
  if (score < 0.30) return { text: "LOW RISK ✅", cls: "risk-low" };
  if (score < 0.60) return { text: "MEDIUM RISK ⚠️", cls: "risk-mid" };
  return { text: "HIGH RISK 🚨", cls: "risk-high" };
}

function decisionSummary(label, score, trusted, breakdown) {
  if (trusted) return "Trusted domain override applied (HTTPS + whitelist).";

  if (label === "phishing") {
    if ((breakdown?.lr ?? 0) > 0.7 && (breakdown?.xgboost ?? 0) > 0.7) {
      return "Both ML models strongly indicate phishing patterns.";
    }
    return "Hybrid score exceeded phishing threshold.";
  } else {
    if (score < 0.20) return "Hybrid score indicates the link is likely safe.";
    return "The link appears safe but remains near borderline risk.";
  }
}

function progressBar(percent) {
  return `
    <div class="confidence-wrap">
      <div class="confidence-bar">
        <div class="confidence-fill" style="width:${percent}%"></div>
      </div>
      <span class="confidence-label">${percent}%</span>
    </div>
  `;
}

function renderResult(type, data) {
  const label = (data.label || "unknown").toUpperCase();
  const score = Number(data.score ?? 0);
  const percent = Math.round(score * 100);

  const exp = data.explanation || {};
  const trusted = exp.trusted_domain === true;
  const breakdown = exp.model_breakdown || {};

  // Risk Level
  const risk = getRiskLevel(score);

  // Summary
  const summaryText = decisionSummary(
    data.label,
    score,
    trusted,
    breakdown
  );

  resultArea.innerHTML = `
    <div class="result-card">
      <div class="result-header">
        <h4>Detection Result</h4>
        <span class="result-badge ${data.label === "phishing" ? "badge-phish" : "badge-legit"}">${label}</span>
      </div>

      <div class="divider"></div>

      <div class="section-block">
        <div class="section-title">📊 Phishing Confidence</div>
        ${progressBar(percent)}
        <div class="small-note">Confidence = final hybrid score × 100</div>
      </div>

      <div class="section-block">
        <div class="section-title">⚡ Risk Level</div>
        <span class="risk-pill ${risk.cls}">${risk.text}</span>
      </div>

      <div class="section-block">
        <div class="section-title">🧾 Decision Summary</div>
        <div class="summary-box">${escapeHTML(summaryText)}</div>
      </div>

      <div class="section-block">
        <div class="section-title">✅ Final Score</div>
        <div class="score-box">${score.toFixed(4)}</div>
      </div>

      <div class="section-block">
        <div class="section-title">🔐 Trusted Domain</div>
        <div>${trusted ? "Yes ✅ (whitelist override applied)" : "No ❌"}</div>
      </div>
    </div>
  `;
}

async function scan(type) {
  const text =
    type === "url"
      ? document.getElementById("urlInput").value.trim()
      : document.getElementById("emailInput").value.trim();

  if (!text) {
    resultArea.innerHTML = `<div class="text-warning">⚠️ Please enter ${type.toUpperCase()} input.</div>`;
    return;
  }

  resultArea.innerHTML = `<div class="text-info">⏳ Scanning ${type.toUpperCase()}...</div>`;

  try {
    const r = await fetch("/api/predict/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type, text })
    });

    const d = await r.json();
    if (!r.ok) throw new Error(d.error || "Request failed");

    renderResult(type, d);

  } catch (e) {
    resultArea.innerHTML = `<div class="text-warning">❌ Error: ${escapeHTML(e.message)}</div>`;
  }
}
