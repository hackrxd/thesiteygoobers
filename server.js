// Import the necessary modules.
const express = require('express');
const path = require('path');
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

const webtextdata = require('./webtextdata.js');

// --- NEW AUTHENTICATION SETUP ---
app.use(session({
    secret: process.env.SESSION_SECRET || 'a-very-secret-key',
    resave: false,
    saveUninitialized: false
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
passport.use(new DiscordStrategy({
    clientID: process.env.CLIENT_ID, // Will now pull from your .env file
    clientSecret: process.env.CLIENT_SECRET, // Will now pull from your .env file
    callbackURL: 'http://localhost:3000/auth/discord/callback',
    scope: ['identify', 'guilds']
}, (accessToken, refreshToken, profile, done) => {
    return done(null, profile);
}));

// --- Static File Serving (Express's built-in way) ---
// Serve static files from the root of your project
app.use(express.static(path.join(__dirname)));
app.use('/uploads', express.static('uploads'));

// --- Route Handling ---
// Discord Authentication Routes
app.get('/auth/discord', passport.authenticate('discord'));

app.get('/auth/discord/callback', 
    passport.authenticate('discord', { failureRedirect: '/login' }),
    (req, res) => {
        res.redirect('/'); 
    }
);

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

app.get('/upload', (req, res) => {
    res.sendFile(path.join(__dirname, 'upload.html'));
});

app.get('/blaine', (req, res) => {
    res.sendFile(path.join(__dirname, 'blaineisverycool.html'));
});

app.get('/events/anonymous', (req, res) => {
    res.sendFile(path.join(__dirname, 'anonymousanomaly.html'));
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