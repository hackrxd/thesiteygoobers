const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const router = express.Router();

// Helper function to sanitize the filename
function sanitizeFilename(filename) {
    const cleanFilename = filename
        .toLowerCase()
        .replace(/[^a-z0-9-.]/g, '-')
        .replace(/^-+|-+$/g, '');

    return cleanFilename;
}

// Create the 'uploads' directory if it doesn't exist
const uploadDir = 'uploads/';
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

// Configure multer for file storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const sanitizedFilename = sanitizeFilename(file.originalname);
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, uniqueSuffix + '-' + sanitizedFilename);
    }
});
const upload = multer({ storage: storage });

// NEW: Middleware to check if the user is authenticated
function isLoggedIn(req, res, next) {
    if (req.isAuthenticated()) {
        return next();
    }
    // If not authenticated, redirect to the login page or send an error
    res.redirect('/auth/discord');
}

// Define the POST route for file uploads
// Note the `isLoggedIn` middleware added here before the `upload.single` call
router.post('/', isLoggedIn, upload.single('my-file'), (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file was uploaded.');
    }
    
    const fileUrl = `/uploads/${req.file.filename}`;
    
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Upload Complete</title>
        </head>
        <body>
            <h1>File Upload Successful!</h1>
            <p>Your file has been saved to the server.</p>
            <p>You can view it here: <a href="${fileUrl}">${req.file.originalname}</a></p>
            <p><a href="/upload">Upload another file</a></p>
        </body>
        </html>
    `);
});

module.exports = router;