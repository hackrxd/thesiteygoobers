// webtextdata.js
// Helper for saving and loading webtext data server-side

const fs = require('fs');
const path = require('path');
const DATA_FILE = path.join(__dirname, 'webtextdata.json');

function saveWebText(data) {
    let allData = [];
    if (fs.existsSync(DATA_FILE)) {
        try {
            allData = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
        } catch (err) {
            allData = [];
        }
    }
    allData.push({ ...data, timestamp: Date.now() });
    fs.writeFileSync(DATA_FILE, JSON.stringify(allData, null, 2));
}

function loadWebText() {
    if (fs.existsSync(DATA_FILE)) {
        try {
            return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
        } catch (err) {
            return [];
        }
    }
    return [];
}

module.exports = { saveWebText, loadWebText };
