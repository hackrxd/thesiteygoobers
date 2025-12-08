// webtextupdate.js (browser-side)

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Convert URLs in plain text into clickable <a> links
function linkify(text) {
    if (!text) return '';

    const urlRegex = /((https?:\/\/)[^\s<]+)/gi;

    return text.replace(urlRegex, (url) => {
        return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
    });
}

function updateQuoteNow() {
    const quoteElem = document.getElementById('willow-quote');
    if (!quoteElem) return;

    fetch('/api/webtextdata')
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data) && data.length > 0) {
                const latest = data[data.length - 1];

                const message = linkify(latest.message || JSON.stringify(latest));
                const author = latest.author || 'Unknown';

                quoteElem.innerHTML = `"${message}" - ${author}`;
            } else {
                quoteElem.textContent = 'No quote found.';
            }
        })
        .catch(() => {
            if (quoteElem) {
                quoteElem.textContent = 'Error loading quote.';
            }
        });
}

// Make sure DOM is ready before the first update
document.addEventListener('DOMContentLoaded', () => {
    updateQuoteNow();
    setInterval(updateQuoteNow, 200);
});
