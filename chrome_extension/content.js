// content.js - Auto popup script (FINAL)
console.log('🛡️ SafeScan content loaded');

// Listen for messages from background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'SHOW_POPUP' && request.data) {
        setTimeout(() => {
            showPopup(request.data);
        }, 1000);
        sendResponse({ success: true });
    }
    return true;
});

function showPopup(data) {
    // Remove existing popup
    const existing = document.getElementById('safescan-popup');
    if (existing) existing.remove();

    // ===============================
    // DETERMINE STATE (IMPORTANT)
    // ===============================
    let title = 'SAFE SITE';
    let bgColor = '#10b981';
    let borderColor = '#0d9668';
    let icon = '✅';
    let message = 'Website appears safe';

    if (data.state === 'PHISHING') {
        title = 'PHISHING DETECTED';
        bgColor = '#ef4444';
        borderColor = '#b91c1c';
        icon = '⚠️';
        message = 'This website has been identified as phishing';

    } else if (data.state === 'SUSPICIOUS') {
        title = 'SUSPICIOUS WEBSITE';
        bgColor = '#f59e0b';
        borderColor = '#b45309';
        icon = '⚠️';
        message = 'This website requires caution';
    }

    // ===============================
    // CREATE POPUP
    // ===============================
    const popup = document.createElement('div');
    popup.id = 'safescan-popup';

    popup.innerHTML = `
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            width: 320px;
            padding: 15px;
            border-radius: 14px;
            font-family: -apple-system, system-ui, sans-serif;
            z-index: 999999;
            animation: slideIn 0.4s ease;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            background: ${bgColor};
            color: white;
            border: 2px solid ${borderColor};
        ">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <div style="font-size:26px;">${icon}</div>
                <div style="font-size:16px;font-weight:700;">${title}</div>
                <button id="closePopup" style="
                    margin-left:auto;
                    background:rgba(255,255,255,0.25);
                    border:none;
                    color:white;
                    width:24px;
                    height:24px;
                    border-radius:50%;
                    cursor:pointer;
                    font-size:16px;
                ">×</button>
            </div>

            <div style="font-size:13px;opacity:0.95;">
                ${message}<br/>
                <small>${data.confidence}% ML confidence</small>
            </div>

            <div style="
                height:4px;
                background:rgba(255,255,255,0.4);
                border-radius:2px;
                margin-top:10px;
                overflow:hidden;
            ">
                <div style="
                    width:100%;
                    height:100%;
                    background:white;
                    animation: shrink 5s linear forwards;
                "></div>
            </div>
        </div>

        <style>
            @keyframes slideIn {
                from { transform: translateX(80px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(80px); opacity: 0; }
            }
            @keyframes shrink {
                from { width:100%; }
                to { width:0%; }
            }
        </style>
    `;

    document.body.appendChild(popup);

    // Close button
    document.getElementById('closePopup').onclick = () => popup.remove();

    // Auto remove after 5s
    setTimeout(() => {
        if (popup.parentNode) popup.remove();
    }, 5000);
}
