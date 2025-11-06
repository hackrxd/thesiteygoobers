const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { notifyUpload } = require('./bot.js');

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

// NOTE: Uploads used to require Discord authentication. We're allowing anonymous uploads
// now. This route no longer applies server-side limits or mime-type filtering
// (per your request: "no limits"). Be aware this increases risk of abuse; consider
// adding protections (rate-limiting, virus scanning, etc.) if this is public.

// Define the POST route for file uploads
// Note: this route accepts anonymous uploads and returns JSON with filename and URL
router.post('/', upload.single('my-file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file was uploaded.' });
    }

    const fileUrl = `/uploads/${req.file.filename}`;
    const uploader = (req.isAuthenticated && req.user) ? `${req.user.username || req.user.id}` : 'anonymous';
    console.log(`Upload saved: ${req.file.filename} (original: ${req.file.originalname}) by ${uploader}`);
    notifyUpload(req.file.originalname, uploader, fileUrl);
    // Respond with JSON containing the original filename and the accessible URL
    res.json({
        originalName: req.file.originalname,
        storedName: req.file.filename,
        fileUrl: fileUrl,
        uploader: uploader
    });
});

module.exports = router;