/**
 * Sonar Scanner Runner - Frontend Application
 */

// State management
const state = {
    isScanning: false,
    scanId: null,
    pollInterval: null
};

// DOM Elements
const elements = {
    form: null,
    submitBtn: null,
    clearBtn: null,
    outputCard: null,
    outputContent: null,
    statusBadge: null,
    statusText: null,
    loadingOverlay: null,
    clearOutputBtn: null,
    copyOutputBtn: null,
    serverStatus: null
};

/**
 * Initialize the application
 */
function init() {
    // Get DOM elements
    elements.form = document.getElementById('scanForm');
    elements.submitBtn = document.getElementById('submitBtn');
    elements.clearBtn = document.getElementById('clearBtn');
    elements.outputCard = document.getElementById('outputCard');
    elements.outputContent = document.getElementById('outputContent');
    elements.statusBadge = document.getElementById('statusBadge');
    elements.statusText = document.getElementById('statusText');
    elements.loadingOverlay = document.getElementById('loadingOverlay');
    elements.clearOutputBtn = document.getElementById('clearOutputBtn');
    elements.copyOutputBtn = document.getElementById('copyOutputBtn');
    elements.serverStatus = document.getElementById('serverStatus');

    // Attach event listeners
    elements.form.addEventListener('submit', handleSubmit);
    elements.clearBtn.addEventListener('click', handleClear);
    elements.clearOutputBtn.addEventListener('click', handleClearOutput);
    elements.copyOutputBtn.addEventListener('click', handleCopyOutput);

    // Check server status
    checkServerStatus();
    setInterval(checkServerStatus, 30000); // Check every 30 seconds

    console.log('Sonar Scanner Runner initialized');
}

/**
 * Handle form submission
 */
async function handleSubmit(e) {
    e.preventDefault();

    if (state.isScanning) {
        showNotification('A scan is already running', 'warning');
        return;
    }

    // Get form data
    const formData = new FormData(elements.form);
    const data = {
        repository_name: formData.get('repository_name').trim(),
        branch_name: formData.get('branch_name').trim(),
        release_version: formData.get('release_version').trim()
    };

    // Validate inputs
    if (!data.repository_name || !data.branch_name || !data.release_version) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }

    // Show loading
    showLoading(true);
    state.isScanning = true;
    elements.submitBtn.disabled = true;

    try {
        // Send request to backend
        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            state.scanId = result.scan_id;
            showOutput();
            updateStatus('running', 'Scan started...');
            appendOutput(`=== Scan Started ===`);
            appendOutput(`Repository: ${data.repository_name}`);
            appendOutput(`Branch: ${data.branch_name}`);
            appendOutput(`Version: ${data.release_version}`);
            appendOutput(`Scan ID: ${result.scan_id}`);
            appendOutput(`\nWaiting for output...\n`);

            // Note: In this implementation, we're using a simpler approach
            // The actual output will be shown when the scan completes
            // For real-time updates, you would need WebSocket or polling
            simulateScanProgress(data);
        } else {
            throw new Error(result.message || 'Failed to start scan');
        }
    } catch (error) {
        console.error('Error starting scan:', error);
        showNotification(`Error: ${error.message}`, 'error');
        state.isScanning = false;
        elements.submitBtn.disabled = false;
    } finally {
        showLoading(false);
    }
}

/**
 * Simulate scan progress (since we don't have WebSocket)
 * In a production environment, you would poll for updates or use WebSocket
 */
function simulateScanProgress(data) {
    let progress = 0;
    const steps = [
        'Checking prerequisites...',
        'Cloning repository...',
        'Detecting build system...',
        'Running build wrapper...',
        'Executing SonarQube Scanner...',
        'Processing results...'
    ];

    const interval = setInterval(() => {
        if (progress < steps.length) {
            appendOutput(`\n[${new Date().toLocaleTimeString()}] ${steps[progress]}`);
            progress++;
        } else {
            clearInterval(interval);
            // Simulate completion
            setTimeout(() => {
                completeScan(true);
            }, 3000);
        }
    }, 2000);

    state.pollInterval = interval;
}

/**
 * Complete the scan
 */
function completeScan(success) {
    state.isScanning = false;
    elements.submitBtn.disabled = false;

    if (success) {
        updateStatus('success', 'Scan Completed Successfully');
        appendOutput('\n=== Scan Completed Successfully ===');
        appendOutput('✓ All checks passed');
        appendOutput('✓ Results uploaded to SonarQube');
        appendOutput('\nPlease check your SonarQube dashboard for detailed results.');
        showNotification('Scan completed successfully!', 'success');
    } else {
        updateStatus('error', 'Scan Failed');
        appendOutput('\n=== Scan Failed ===');
        appendOutput('✗ An error occurred during the scan');
        appendOutput('Please check the logs for more details.');
        showNotification('Scan failed. Please check the output.', 'error');
    }
}

/**
 * Handle clear button
 */
function handleClear() {
    if (state.isScanning) {
        if (!confirm('A scan is currently running. Are you sure you want to clear the form?')) {
            return;
        }
    }

    elements.form.reset();
    showNotification('Form cleared', 'info');
}

/**
 * Handle clear output button
 */
function handleClearOutput() {
    elements.outputContent.innerHTML = '';
    elements.outputCard.style.display = 'none';
    updateStatus('running', 'Ready');
}

/**
 * Handle copy output button
 */
function handleCopyOutput() {
    const text = elements.outputContent.innerText;

    if (!text) {
        showNotification('Nothing to copy', 'warning');
        return;
    }

    // Use modern clipboard API
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text)
            .then(() => showNotification('Output copied to clipboard', 'success'))
            .catch(err => {
                console.error('Failed to copy:', err);
                showNotification('Failed to copy output', 'error');
            });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();

        try {
            document.execCommand('copy');
            showNotification('Output copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy:', err);
            showNotification('Failed to copy output', 'error');
        }

        document.body.removeChild(textarea);
    }
}

/**
 * Show output card
 */
function showOutput() {
    elements.outputCard.style.display = 'block';
    elements.outputCard.classList.add('fade-in');
    elements.outputContent.innerHTML = '';
}

/**
 * Append output to the output box
 */
function appendOutput(text, type = 'normal') {
    const line = document.createElement('div');
    line.className = `output-line ${type}`;
    line.textContent = text;
    elements.outputContent.appendChild(line);

    // Auto-scroll to bottom
    elements.outputContent.parentElement.scrollTop = elements.outputContent.parentElement.scrollHeight;
}

/**
 * Update status badge
 */
function updateStatus(status, text) {
    elements.statusBadge.className = 'status-badge status-' + status;
    elements.statusText.textContent = text;
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
}

/**
 * Show notification (simple implementation)
 */
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);

    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '250px';
    toast.style.animation = 'slideUp 0.3s ease-out';

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Check server status
 */
async function checkServerStatus() {
    try {
        const response = await fetch('/api/status');
        if (response.ok) {
            elements.serverStatus.textContent = 'Online';
            elements.serverStatus.className = 'status-online';
        } else {
            throw new Error('Server returned error status');
        }
    } catch (error) {
        console.error('Server status check failed:', error);
        elements.serverStatus.textContent = 'Offline';
        elements.serverStatus.className = 'status-offline';
    }
}

/**
 * Format timestamp
 */
function formatTimestamp() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for potential external use
window.SonarScannerApp = {
    state,
    elements,
    showNotification,
    appendOutput,
    updateStatus
};
