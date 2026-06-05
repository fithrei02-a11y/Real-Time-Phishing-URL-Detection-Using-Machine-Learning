console.log("🛡️ SafeScan background loaded");

// Track popup per tab + domain
let shownDomains = {};

// ===============================
// MACHINE LEARNING CHECK
// ===============================
async function checkUrlWithML(url) {
  try {
    const res = await fetch("http://localhost:5000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": "FYP_SECRET_2026"
      },
      body: JSON.stringify({ url })
    });

    if (!res.ok) throw new Error("Server error");

    const data = await res.json();

    return {
      safe: data.prediction !== "phishing",
      confidence: Math.round(data.confidence * 100),
      explanations: data.explanations || []
    };

  } catch (e) {
    console.warn("⚠️ ML server offline or unauthorized");
    return {
      error: true,
      message: "ML server offline"
    };
  }
}

// ===============================
// CLASSIFICATION LOGIC
// ===============================
function classifyState(result) {
  if (result.error) return "ERROR";

  if (!result.safe) return "PHISHING";

  if (result.confidence < 50) return "SUSPICIOUS";

  return "SAFE";
}

// ===============================
// FINAL CHECK FUNCTION
// ===============================
async function checkUrl(url) {
  const ml = await checkUrlWithML(url);

  if (ml.error) {
    return {
      error: true,
      message: "ML server is offline"
    };
  }

  const state = classifyState(ml);

  return {
    safe: ml.safe,
    confidence: ml.confidence,
    state,
    explanations: ml.explanations,
    message:
      state === "PHISHING"
        ? "Phishing detected by machine learning"
        : state === "SUSPICIOUS"
        ? "Website appears suspicious due to low confidence"
        : "Website appears safe",
    source: "machine-learning"
  };
}

// ===============================
// HANDLE POPUP REQUEST
// ===============================
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "CHECK_URL") {
    checkUrl(request.url).then(sendResponse);
    return true;
  }
});

// ===============================
// AUTO POPUP WHEN PAGE LOADS
// ===============================
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== "complete" || !tab.url) return;

  if (tab.url.startsWith("chrome://")) return;

  if (isSearchPage(tab.url)) return;

  try {
    const hostname = new URL(tab.url).hostname.replace("www.", "");
    const key = `${tabId}-${hostname}`;

    if (shownDomains[key]) return;
    shownDomains[key] = true;

    checkUrl(tab.url).then((result) => {
      if (result.error) return;

      chrome.tabs.sendMessage(tabId, {
        type: "SHOW_POPUP",
        data: result
      }).catch(() => {});
    });

  } catch {}
});

// ===============================
// SEARCH PAGE FILTER
// ===============================
function isSearchPage(url) {
  try {
    const u = new URL(url);

    return (
      (u.hostname.includes("google.") && u.pathname.startsWith("/search")) ||
      (u.hostname.includes("bing.") && u.pathname.startsWith("/search")) ||
      (u.hostname.includes("yahoo.") && u.pathname.startsWith("/search"))
    );

  } catch {
    return true;
  }
}

// ===============================
// CLEANUP
// ===============================
chrome.tabs.onRemoved.addListener((tabId) => {
  Object.keys(shownDomains).forEach((key) => {
    if (key.startsWith(`${tabId}-`)) {
      delete shownDomains[key];
    }
  });
});