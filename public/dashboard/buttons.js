function reboot() {
    areyousure = confirm("Are you sure you want to reboot the system?");
    if (areyousure) {
        fetch('/api/system/reboot', { method: 'POST' })
    }
}

function rename() {
    const newName = prompt("Enter new hostname:");
    if (newName) {
        fetch('/api/system/rename', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: newName })
        })
    }
}

function pauseButton() {
    pauseUpdates()
}

function addDisk() {
    location.href = '/api/create/disk'
}

function changeLog() {
    const newSize = prompt("Enter maximum number of log lines to keep (e.g., 10000):");
    const sizeInt = parseInt(newSize);
    if (!isNaN(sizeInt) && sizeInt > 0) {
        fetch('/api/config/edit/log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ logLines: sizeInt })
        }).then(() => {
            alert(`Log size updated to ${sizeInt} lines.`);
        });
    } else {
        alert("Invalid number entered.");
    }
}

function config() {
    location.href = 'http://192.168.1.60:3000/config/edit'
}

function downloadLog() {
    location.href = 'http://192.168.1.60:3000/log/download';
}

function downloadUpdateLog() {
  location.href = 'http://192.168.1.60:3000/update.log';
}

function switchToGraph() {
    window.open('http://192.168.1.60:3000/graphview', '_blank');
}

function update() {
    fetch('http://192.168.1.60:3000/system/updates/check', { method: 'GET' });
    fetch('http://192.168.1.60:3000/system/updates/apply', { method: 'POST' });
}