// webtextupdate.js (browser-side)

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Convert URLs in plain text into clickable <a> links
// function linkify(text) {
//     if (!text) return '';

//     const urlRegex = /((https?:\/\/)[^\s<]+)/gi;

//     return text.replace(urlRegex, (url) => {
//         return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
//     });
// }


function updateQuoteNow() {
    const quoteElem = document.getElementById('willow-quote');
    if (!quoteElem) return;

    fetch('/api/webtextdata')
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data) && data.length > 0) {
                const latest = data[data.length - 1];

                // FIX: Define the message variable
                const message = latest.message || JSON.stringify(latest);
                const author = latest.author || 'Unknown';

                // --- START Change Detection Logic ---
                if (message === lastMessageContent) {
                    // console.log("Quote hasn't changed, skipping DOM update.");
                    return; // Stop execution if the message is the same
                }
                
                // Update the stored message content
                lastMessageContent = message; 
                // --- END Change Detection Logic ---


                // Only update the DOM if the message changed
                quoteElem.innerHTML = `"${message}" - ${author}`;
                
            } else {
                // If there's no quote, check if we need to update the display
                if (lastMessageContent !== 'No quote found.') {
                    quoteElem.textContent = 'No quote found.';
                    lastMessageContent = 'No quote found.';
                }
            }
        })
        .catch(() => {
            if (quoteElem) {
                 // Error handling message
                const errorMessage = 'Error loading quote.';
                if (lastMessageContent !== errorMessage) {
                    quoteElem.textContent = errorMessage;
                    lastMessageContent = errorMessage;
                }
            }
        });
}
// Make sure DOM is ready before the first update
document.addEventListener('DOMContentLoaded', () => {
    updateQuoteNow();
    setInterval(updateQuoteNow, 200);
});
