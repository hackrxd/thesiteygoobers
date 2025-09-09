// script.js
document.addEventListener('DOMContentLoaded', () => {
    const authContainer = document.getElementById('auth-container');

    fetch('/api/user')
        .then(response => response.json())
        .then(data => {
            if (data.isAuthenticated) {
                authContainer.innerHTML = `
                    <div class="user-info">
                        <span>Logged in as: ${data.username}#${data.discriminator}</span>
                        <a href="/logout">Logout</a>
                    </div>
                `;
            } else {
                authContainer.innerHTML = `
                    <a href="/auth/discord"><button>Login with Discord</button></a>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching user status:', error);
            authContainer.innerHTML = `
                <a href="/auth/discord"><button>Login with Discord</button></a>
            `;
        });
});