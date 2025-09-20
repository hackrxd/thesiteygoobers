
// webtextupdate.js (browser-side)
document.addEventListener('DOMContentLoaded', () => {
    const quoteElem = document.getElementById('willow-quote');
    if (!quoteElem) return;

    fetch('/api/webtextdata')
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data) && data.length > 0) {
                // Get the latest message
                const latest = data[data.length - 1];
                quoteElem.textContent = `"${latest.message || JSON.stringify(latest)}" - ${latest.author}`;
            } else {
                quoteElem.textContent = 'No quote found.';
            }
        })
        .catch(error => {
            quoteElem.textContent = 'Error loading quote.';
        });
});
