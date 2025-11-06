// Import the necessary modules.
const express = require('express');
const path = require('path');
const fs = require('fs');
const uploadRouter = require('./upload.js');
const session = require('express-session');
const passport = require('passport');
const DiscordStrategy = require('passport-discord').Strategy;
const dotenv = require('dotenv');
const bot = require('./bot.js'); // Ensure the bot is started
const anonymous = require('./anonymousanomaly.js');
// --- Add this line here ---
dotenv.config();

// Define the port the server will run on.
const port = 3000;

// Create an Express application.
const app = express();
app.use(express.json()); // For parsing JSON bodies

// Simple ANSI color helper (no extra dependency)
function colorize(text, color) {
    const codes = {
        reset: '\x1b[0m',
        bold: '\x1b[1m',
        dim: '\x1b[2m',
        red: '\x1b[31m',
        green: '\x1b[32m',
        yellow: '\x1b[33m',
        blue: '\x1b[34m',
        magenta: '\x1b[35m',
        cyan: '\x1b[36m'
    };
    const open = codes[color] || '';
    const close = codes.reset;
    return open + text + close;
}

// Enhanced request logging middleware with colorized output and download progress
app.use((req, res, next) => {
    const start = process.hrtime.bigint();
    const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress || req.ip;
    const user = (req && req.user && (req.user.username || req.user.id)) ? (req.user.username || req.user.id) : 'anonymous';
    const method = req.method;
    const url = req.originalUrl || req.url;

    // Track streaming bytes written for downloads
    let bytesSent = 0;
    let totalBytes = null;
    let progressInterval = null;
    let downloadDetected = false;

    // If this is a GET for a file under /uploads, try to read its size from disk so we can show percentage
    if (method === 'GET' && url.startsWith('/uploads')) {
        const filePath = path.join(__dirname, url);
        fs.stat(filePath, (err, stats) => {
            if (!err && stats && typeof stats.size === 'number') {
                totalBytes = stats.size;
            }
        });
    }

    // Save originals
    const origWrite = res.write;
    const origEnd = res.end;

    // Wrap write to count bytes
    res.write = function (chunk, encoding, callback) {
        try {
            const len = chunk ? Buffer.byteLength(chunk instanceof Buffer ? chunk : String(chunk), encoding) : 0;
            bytesSent += len;
        } catch (e) {
            // ignore
        }

        // Try to get total bytes from header if available
        if (!totalBytes) {
            const cl = res.getHeader && res.getHeader('content-length');
            totalBytes = cl ? parseInt(cl, 10) : null;
        }

        // If this looks like a download (uploads folder or content-disposition) start progress logs
        if (!downloadDetected && (url.startsWith('/uploads') || (res.getHeader && res.getHeader('content-disposition')) || totalBytes)) {
            downloadDetected = true;
            progressInterval = setInterval(() => {
                const pct = totalBytes ? ` (${((bytesSent/totalBytes)*100).toFixed(1)}%)` : '';
                console.log(colorize(`[DOWNLOAD] ${method} ${url} - ${bytesSent} bytes${totalBytes ? ` / ${totalBytes}` : ''}${pct}`,'cyan'));
            }, 1000);
        }

        return origWrite.apply(res, arguments);
    };

    // Wrap end to finalize logs
    res.end = function (chunk, encoding, callback) {
        if (chunk) {
            try {
                const len = Buffer.byteLength(chunk instanceof Buffer ? chunk : String(chunk), encoding);
                bytesSent += len;
            } catch (e) {}
        }

        if (!totalBytes) {
            const cl = res.getHeader && res.getHeader('content-length');
            totalBytes = cl ? parseInt(cl, 10) : null;
        }

        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }

        const end = process.hrtime.bigint();
        const durationMs = Number(end - start) / 1e6;
        const time = new Date().toISOString();
        const status = res.statusCode || 0;
        const statusColor = status >= 500 ? 'red' : (status >= 400 ? 'yellow' : 'green');

        console.log(`${colorize(time,'dim')} ${colorize(method,'magenta')} ${colorize(url,'bold')} ${colorize(String(status), statusColor)} ${colorize(durationMs.toFixed(2)+'ms','dim')} - ${ip} - user: ${user}`);

        if (downloadDetected) {
            const pctComplete = totalBytes ? ` (${((bytesSent/totalBytes)*100).toFixed(1)}%)` : '';
            console.log(colorize(`[DOWNLOAD COMPLETE] ${method} ${url} - ${bytesSent} bytes${pctComplete} in ${durationMs.toFixed(2)}ms`,'cyan'));
        }

        return origEnd.apply(res, arguments);
    };

    // Ensure interval cleared on close
    res.on('close', () => {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
            console.log(colorize(`[DOWNLOAD ABORTED] ${method} ${url} - ${bytesSent} bytes sent`,'yellow'));
        }
    });

    // Initial log
    console.log(colorize(`${new Date().toISOString()} ${method} ${url} - started - ${ip} - user: ${user}`,'dim'));

    next();
});

const webtextdata = require('./webtextdata.js');

// --- NEW AUTHENTICATION SETUP ---
app.use(session({
    secret: process.env.SESSION_SECRET || 'a-very-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: process.env.NODE_ENV === 'production',
        maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
}));
app.use(passport.initialize());
app.use(passport.session());

// Passport serialization and deserialization
passport.serializeUser((user, done) => {
    done(null, user);
});

passport.deserializeUser((obj, done) => {
    done(null, obj);
});

// Configure the Discord strategy
// Prefer using env vars; allow skipping Discord auth if not configured so the server can run
const discordClientId = process.env.CLIENT_ID;
const discordClientSecret = process.env.CLIENT_SECRET;
const discordCallbackURL = process.env.CALLBACK_URL || 'http://localhost:3000/auth/discord/callback';

console.log('Configuring Discord strategy with:', {
    clientID: discordClientId ? `${discordClientId.slice(0, 4)}...${discordClientId.slice(-4)}` : undefined,
    callbackURL: discordCallbackURL
});

if (discordClientId && discordClientSecret) {
    passport.use(new DiscordStrategy({
        clientID: discordClientId,
        clientSecret: discordClientSecret,
        callbackURL: discordCallbackURL,
        scope: ['identify'],
        // state: false, // usually leave state enabled for security
        passReqToCallback: true
    }, async (req, accessToken, refreshToken, profile, done) => {
    try {
        console.log('Auth callback received');
            console.log('Profile:', profile);
        
        if (!profile) {
            console.log('No profile received');
            return done(new Error('No profile received from Discord'), null);
        }

        // Store tokens in the user profile
        profile.accessToken = accessToken;
        profile.refreshToken = refreshToken;
        return done(null, profile);
    } catch (err) {
        console.error('Error in Discord strategy:', err);
        return done(err, null);
    }
}));

} else {
    console.warn('Discord CLIENT_ID and/or CLIENT_SECRET not set. Discord authentication routes will be unavailable until these are provided. Create a .env file or set CLIENT_ID and CLIENT_SECRET in the environment.');
}

// Authentication middleware
function isAuthenticated(req, res, next) {
    if (req.isAuthenticated()) {
        return next();
    }
    res.status(401).json({ error: 'Not authenticated' });
}

// --- Static File Serving (Express's built-in way) ---
// Serve static files from the root of your project
app.use(express.static(path.join(__dirname)));
app.use('/uploads', express.static('uploads'));

// --- Route Handling ---
// Discord Authentication Routes
app.get('/auth/discord', (req, res, next) => {
    // Store the return URL if provided
    if (req.query.returnTo) {
        req.session.returnTo = req.query.returnTo;
    }
    passport.authenticate('discord', {
        prompt: 'consent'
    })(req, res, next);
});

app.get('/auth/discord/callback', (req, res, next) => {
    console.log('Received callback request');
    console.log('Query params:', req.query);
    
    passport.authenticate('discord', { 
        failureRedirect: '/login',
        failureMessage: true
    })(req, res, (err) => {
        if (err) {
            console.error('Authentication error:', err);
            return res.redirect('/login?error=' + encodeURIComponent(err.message));
        }
        
        console.log('Authentication successful');
        const returnTo = req.session.returnTo || '/';
        delete req.session.returnTo;
        res.redirect(returnTo);
    });
});

app.get('/profile', (req, res) => {
    if (req.isAuthenticated()) {
        res.send(`<h1>Hello, ${req.user.username}#${req.user.discriminator}</h1>
        <img src="https://cdn.discordapp.com/avatars/${req.user.id}/${req.user.avatar}.png" alt="Avatar" width="100">
        <p>Your Discord ID: ${req.user.id}</p>
        <a href="/logout">Logout</a>`);
    } else {
        res.redirect('/login');
    }
});

app.get('/logout', (req, res) => {
    req.logout((err) => {
        if (err) { return next(err); }
        res.redirect('/');
    });
});

// Regular Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/staff', (req, res) => {
    res.sendFile(path.join(__dirname, 'staff.html'));
});

app.get('/staff/skitters', (req, res) => {
    res.sendFile(path.join(__dirname, 'skitters.html'));
});

app.get('/staff/hackrxd', (req, res) => {
    res.sendFile(path.join(__dirname, 'hackr.html'));
});

// User status endpoint
app.get('/api/user', (req, res) => {
    if (req.isAuthenticated()) {
        res.json({
            isAuthenticated: true,
            username: req.user.username,
            discriminator: req.user.discriminator,
            id: req.user.id,
            avatar: req.user.avatar
        });
    } else {
        res.json({ isAuthenticated: false });
    }
});

app.get('/upload', (req, res) => {
    res.sendFile(path.join(__dirname, 'upload.html'));
});

app.get('/blaine', (req, res) => {
    res.sendFile(path.join(__dirname, 'blaineisverycool.html'));
});

app.get('/events/anonymous', (req, res) => {
    res.sendFile(path.join(__dirname, 'anonymousanomaly.html'));
});

app.get('/events', (req, res) => {
    res.sendFile(path.join(__dirname, 'events.html'));
});

// API endpoint to receive POST requests and forward to webtextupdate.js

// Save incoming webtext data to JSON file
app.post('/api/webtext', (req, res) => {
    try {
        webtextdata.saveWebText(req.body);
        res.status(200).json({ status: 'success' });
    } catch (err) {
        res.status(500).json({ status: 'error', error: err.message });
    }
});

// GET endpoint for browser-side code to fetch all webtext data
app.get('/api/webtextdata', (req, res) => {
    try {
        const data = webtextdata.loadWebText();
        res.status(200).json(data);
    } catch (err) {
        res.status(500).json({ status: 'error', error: err.message });
    }
});

// Mount the upload router at the '/upload' path.
app.use('/upload', uploadRouter);

// 404 handler for all other routes
app.use((req, res) => {
    res.status(404).sendFile(path.join(__dirname, '404.html'));
    // If you don't have a 404.html, uncomment the next line:
    // res.status(404).send('404 Not Found');
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}/`);
});