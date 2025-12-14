// webtextupdate.js (browser-side)

// Store the last received quote message to detect changes
let lastMessageContent = null; 

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

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
    // You might want to increase the interval since updates are now conditional
    // 200ms is still very fast. I recommend 500ms or 1000ms (1 second)
    updateQuoteNow();
    setInterval(updateQuoteNow, 1000); // Changed to 1 second interval
});