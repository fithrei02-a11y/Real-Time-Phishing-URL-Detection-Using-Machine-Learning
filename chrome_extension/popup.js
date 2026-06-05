document.addEventListener('DOMContentLoaded', function () {
  const statusEl = document.getElementById('status');
  const urlEl = document.getElementById('url');
  const checkBtn = document.getElementById('checkBtn');

  // ===============================
  // MANUAL CHECK
  // ===============================
  checkBtn.addEventListener('click', function () {
    this.innerHTML = '<span>⏳</span> Checking...';
    this.disabled = true;

    checkCurrentPage();

    setTimeout(() => {
      this.innerHTML = '<span>🔄</span> Check Current Page';
      this.disabled = false;
    }, 2000);
  });

  function checkCurrentPage() {
    statusEl.className = 'status-box';
    statusEl.innerHTML = `
      <div class="status-icon">⏳</div>
      <div class="status-text">Checking...</div>
    `;

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs || !tabs[0] || !tabs[0].url) {
        showError("Unable to read current tab");
        return;
      }

      const url = tabs[0].url;
      urlEl.textContent = shortenUrl(url);

      chrome.runtime.sendMessage(
        { type: 'CHECK_URL', url },
        (result) => {
          if (!result || result.error) {
            showError(result?.message || "ML server not responding");
            return;
          }
          updateStatus(result);
        }
      );
    });
  }

  // ===============================
  // UPDATE UI BASED ON STATE
  // ===============================
  function updateStatus(result) {
    let icon = '';
    let label = '';
    let cssClass = '';
    let explanationHtml = '';

    if (result.state === "PHISHING") {
      icon = '⚠️';
      label = 'PHISHING';
      cssClass = 'phishing';
    } 
    else if (result.state === "SUSPICIOUS") {
      icon = '⚠️';
      label = 'SUSPICIOUS';
      cssClass = 'warning';

      explanationHtml = `
        <div style="margin-top:10px;font-size:11px;text-align:left;">
          <strong>Why this result:</strong>
          <ul style="padding-left:16px;margin:6px 0;">
            <li>• Prediction confidence is borderline (${result.confidence}%)</li>
            <li>• No strong phishing indicators detected</li>
          </ul>
        </div>
      `;
    } 
    else {
      icon = '✅';
      label = 'SAFE';
      cssClass = 'safe';
    }

    // ML explanations (ONLY for phishing)
    if (result.state === "PHISHING" && result.explanations?.length) {
      explanationHtml = `
        <div style="margin-top:10px;font-size:11px;text-align:left;">
          <strong>Why this result:</strong>
          <ul style="padding-left:16px;margin:6px 0;">
            ${result.explanations.map(e => `<li>• ${e}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    statusEl.className = `status-box ${cssClass}`;
    statusEl.innerHTML = `
      <div class="status-icon">${icon}</div>
      <div class="status-text">${label}</div>
      <div class="confidence">${result.confidence}% ML confidence</div>
      ${explanationHtml}
    `;
  }

  function showError(msg) {
    statusEl.className = 'status-box';
    statusEl.innerHTML = `
      <div class="status-icon">⚠️</div>
      <div class="status-text">${msg}</div>
    `;
  }

  function shortenUrl(url) {
    try {
      return new URL(url).hostname.replace(/^www\./, '');
    } catch {
      return url.substring(0, 30) + (url.length > 30 ? '...' : '');
    }
  }
});
