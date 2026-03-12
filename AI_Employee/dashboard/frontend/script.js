/**
 * AI Employee Vault - Dashboard JavaScript
 * Connects frontend to backend API
 */

// API Base URL
const API_BASE = 'http://localhost:8000/api';

// ============================================
// EMAIL MESSAGING FUNCTIONS
// ============================================

/**
 * Send email
 */
async function sendEmail() {
    const to = document.getElementById('email-to').value.trim();
    const subject = document.getElementById('email-subject').value.trim();
    const body = document.getElementById('email-body').value.trim();
    
    if (!to || !subject || !body) {
        showToast('Please fill in all fields', 'warning');
        return;
    }
    
    // Validate email
    if (!to.includes('@')) {
        showToast('Please enter a valid email address', 'warning');
        return;
    }
    
    const button = event.target.closest('button');
    const originalText = button.innerHTML;
    
    // Show loading state
    button.classList.add('btn-loading');
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending...';
    
    try {
        const response = await fetch(`${API_BASE}/email/send-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                to: to,
                subject: subject,
                body: body
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message || 'Email sent!', 'success');
            // Clear fields
            document.getElementById('email-to').value = '';
            document.getElementById('email-subject').value = '';
            document.getElementById('email-body').value = '';
            // Load sent emails
            loadSentEmails();
        } else {
            showToast(data.detail || 'Failed to send email', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        // Reset button
        button.classList.remove('btn-loading');
        button.innerHTML = originalText;
    }
}

/**
 * Load sent emails
 */
async function loadSentEmails() {
    const container = document.getElementById('email-sent');
    
    container.innerHTML = '<div class="flex items-center justify-center h-full"><i class="fas fa-spinner fa-spin text-red-600 text-2xl"></i></div>';
    
    try {
        const response = await fetch(`${API_BASE}/email/sent`);
        const data = await response.json();
        
        if (response.ok && data.emails && data.emails.length > 0) {
            let html = '<div class="space-y-3">';
            
            data.emails.forEach(email => {
                const statusColors = {
                    'sent': 'text-green-600',
                    'queued': 'text-blue-600',
                    'failed': 'text-red-600'
                };
                
                const statusClass = statusColors[email.status] || 'text-gray-600';
                
                html += `
                    <div class="bg-white rounded p-3 border border-gray-200">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-sm font-semibold text-gray-700">
                                <i class="fas fa-envelope text-red-600 mr-1"></i>${email.to}
                            </span>
                            <span class="text-xs ${statusClass}">${email.status}</span>
                        </div>
                        <p class="text-sm font-medium text-gray-800 mb-1">${email.subject}</p>
                        <p class="text-xs text-gray-600 mb-2">${email.body}</p>
                        <span class="text-xs text-gray-400">${formatTimestamp(email.timestamp)}</span>
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = `
                <div class="text-gray-400 text-center py-8">
                    <i class="fas fa-inbox text-3xl mb-2"></i>
                    <p class="text-sm">No sent emails</p>
                </div>
            `;
        }
    } catch (error) {
        container.innerHTML = `
            <div class="text-red-500 text-center py-8">
                <i class="fas fa-exclamation-circle text-3xl mb-2"></i>
                <p class="text-sm">Error loading emails</p>
            </div>
        `;
    }
}

// ============================================
// INSTAGRAM MESSAGING FUNCTIONS
// ============================================

/**
 * Send Instagram DM
 */
async function sendInstagramDM() {
    const username = document.getElementById('ig-username').value.trim();
    const message = document.getElementById('ig-message').value.trim();
    
    if (!username || !message) {
        showToast('Please enter username and message', 'warning');
        return;
    }
    
    const button = event.target.closest('button');
    const originalText = button.innerHTML;
    
    // Show loading state
    button.classList.add('btn-loading');
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending...';
    
    try {
        const response = await fetch(`${API_BASE}/instagram/send-dm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                message: message
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message || 'Instagram DM sent!', 'success');
            // Clear fields
            document.getElementById('ig-username').value = '';
            document.getElementById('ig-message').value = '';
            // Load sent DMs
            loadInstagramDMs();
        } else {
            showToast(data.detail || 'Failed to send DM', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        // Reset button
        button.classList.remove('btn-loading');
        button.innerHTML = originalText;
    }
}

/**
 * Load Instagram DMs
 */
async function loadInstagramDMs() {
    const container = document.getElementById('ig-sent-dms');
    
    container.innerHTML = '<div class="flex items-center justify-center h-full"><i class="fas fa-spinner fa-spin text-pink-600 text-2xl"></i></div>';
    
    try {
        const response = await fetch(`${API_BASE}/instagram/messages`);
        const data = await response.json();
        
        if (response.ok && data.messages && data.messages.length > 0) {
            let html = '<div class="space-y-3">';
            
            data.messages.forEach(msg => {
                const statusColors = {
                    'sent': 'text-green-600',
                    'queued': 'text-blue-600',
                    'failed': 'text-red-600'
                };
                
                const statusClass = statusColors[msg.status] || 'text-gray-600';
                
                html += `
                    <div class="bg-white rounded p-3 border border-gray-200">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-sm font-semibold text-gray-700">
                                <i class="fab fa-instagram text-pink-600 mr-1"></i>@${msg.username}
                            </span>
                            <span class="text-xs ${statusClass}">${msg.status}</span>
                        </div>
                        <p class="text-sm text-gray-600 mb-2">${msg.message}</p>
                        <span class="text-xs text-gray-400">${formatTimestamp(msg.timestamp)}</span>
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = `
                <div class="text-gray-400 text-center py-8">
                    <i class="fas fa-paper-plane text-3xl mb-2"></i>
                    <p class="text-sm">No sent DMs</p>
                </div>
            `;
        }
    } catch (error) {
        container.innerHTML = `
            <div class="text-red-500 text-center py-8">
                <i class="fas fa-exclamation-circle text-3xl mb-2"></i>
                <p class="text-sm">Error loading DMs</p>
            </div>
        `;
    }
}

// ============================================
// WHATSAPP MESSAGING FUNCTIONS
// ============================================

/**
 * Send WhatsApp message
 */
async function sendWhatsApp() {
    const countryCode = document.getElementById('wa-country-code').value;
    const phone = document.getElementById('wa-phone').value.trim();
    const message = document.getElementById('wa-message').value.trim();
    
    if (!phone || !message) {
        showToast('Please enter phone number and message', 'warning');
        return;
    }
    
    const button = event.target.closest('button');
    const originalText = button.innerHTML;
    
    // Show loading state
    button.classList.add('btn-loading');
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending...';
    
    try {
        const response = await fetch(`${API_BASE}/whatsapp/send-whatsapp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phone: phone,
                message: message,
                country_code: countryCode
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message || 'WhatsApp message sent!', 'success');
            // Clear message field
            document.getElementById('wa-message').value = '';
            // Load recent messages
            loadWhatsAppMessages();
        } else {
            showToast(data.detail || 'Failed to send message', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        // Reset button
        button.classList.remove('btn-loading');
        button.innerHTML = originalText;
    }
}

/**
 * Load WhatsApp messages
 */
async function loadWhatsAppMessages() {
    const container = document.getElementById('wa-recent-messages');
    
    container.innerHTML = '<div class="flex items-center justify-center h-full"><i class="fas fa-spinner fa-spin text-green-600 text-2xl"></i></div>';
    
    try {
        const response = await fetch(`${API_BASE}/whatsapp/messages`);
        const data = await response.json();
        
        if (response.ok && data.messages && data.messages.length > 0) {
            let html = '<div class="space-y-3">';
            
            data.messages.forEach(msg => {
                const statusColors = {
                    'sent': 'text-green-600',
                    'pending': 'text-yellow-600',
                    'queued': 'text-blue-600',
                    'failed': 'text-red-600'
                };
                
                const statusIcons = {
                    'sent': 'fa-check-circle',
                    'pending': 'fa-clock',
                    'queued': 'fa-hourglass-half',
                    'failed': 'fa-times-circle'
                };
                
                const statusClass = statusColors[msg.status] || 'text-gray-600';
                const statusIcon = statusIcons[msg.status] || 'fa-circle';
                
                html += `
                    <div class="bg-white rounded p-3 border border-gray-200">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-sm font-semibold text-gray-700">
                                <i class="fab fa-whatsapp text-green-600 mr-1"></i>${msg.phone}
                            </span>
                            <span class="text-xs ${statusClass}">
                                <i class="fas ${statusIcon}"></i> ${msg.status}
                            </span>
                        </div>
                        <p class="text-sm text-gray-600 mb-2">${msg.message}</p>
                        <span class="text-xs text-gray-400">${formatTimestamp(msg.timestamp)}</span>
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = `
                <div class="text-gray-400 text-center py-8">
                    <i class="fas fa-comments text-3xl mb-2"></i>
                    <p class="text-sm">No recent messages</p>
                </div>
            `;
        }
    } catch (error) {
        container.innerHTML = `
            <div class="text-red-500 text-center py-8">
                <i class="fas fa-exclamation-circle text-3xl mb-2"></i>
                <p class="text-sm">Error loading messages</p>
            </div>
        `;
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Toggle Dark Mode
 */
function toggleDarkMode() {
    const html = document.documentElement;
    const isDark = html.classList.toggle('dark');
    
    // Save preference to localStorage
    localStorage.setItem('darkMode', isDark ? 'true' : 'false');
    
    // Update sidebar gradient
    const sidebar = document.querySelector('aside');
    if (isDark) {
        sidebar.classList.remove('sidebar-gradient');
        sidebar.classList.add('sidebar-gradient-dark');
    } else {
        sidebar.classList.remove('sidebar-gradient-dark');
        sidebar.classList.add('sidebar-gradient');
    }
}

/**
 * Initialize Dark Mode from localStorage
 */
function initDarkMode() {
    const isDark = localStorage.getItem('darkMode') === 'true';
    const html = document.documentElement;
    const sidebar = document.querySelector('aside');
    
    if (isDark) {
        html.classList.add('dark');
        sidebar.classList.remove('sidebar-gradient');
        sidebar.classList.add('sidebar-gradient-dark');
    } else {
        html.classList.remove('dark');
        sidebar.classList.remove('sidebar-gradient-dark');
        sidebar.classList.add('sidebar-gradient');
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = toast.querySelector('i');
    
    // Set icon based on type
    const icons = {
        info: 'fa-info-circle',
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle'
    };
    
    toastIcon.className = `fas ${icons[type] || icons.info} mr-2`;
    toastMessage.textContent = message;
    
    // Show toast
    toast.classList.remove('translate-y-20', 'opacity-0');
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
    }, 3000);
}

/**
 * Check API connection
 */
async function checkConnection() {
    const statusDot = document.getElementById('connection-status');
    const statusText = document.getElementById('connection-text');
    
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            statusDot.classList.remove('bg-red-500');
            statusDot.classList.add('bg-green-500');
            statusText.textContent = 'Connected';
            return true;
        }
    } catch (error) {
        statusDot.classList.remove('bg-green-500');
        statusDot.classList.add('bg-red-500');
        statusText.textContent = 'Disconnected';
    }
    return false;
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString();
}

// ============================================
// WATCHERS FUNCTIONS
// ============================================

/**
 * Start a watcher
 */
async function startWatcher(watcherName) {
    const button = event.target;
    const originalText = button.innerHTML;
    
    // Show loading state
    button.classList.add('btn-loading');
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Starting...';
    
    try {
        const response = await fetch(`${API_BASE}/watchers/start-${watcherName}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(`${watcherName} watcher started!`, 'success');
            updateWatcherStatus(watcherName, true);
        } else {
            showToast(data.detail || 'Failed to start watcher', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        // Reset button
        button.classList.remove('btn-loading');
        button.innerHTML = originalText;
    }
}

/**
 * Stop all watchers
 */
async function stopAllWatchers() {
    if (!confirm('Are you sure you want to stop all watchers?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/watchers/stop-watchers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('All watchers stopped', 'success');
            // Update all status indicators
            ['gmail', 'whatsapp', 'instagram', 'linkedin'].forEach(name => {
                updateWatcherStatus(name, false);
            });
        } else {
            showToast(data.detail || 'Failed to stop watchers', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Update watcher status indicator
 */
function updateWatcherStatus(watcherName, isRunning) {
    const statusElement = document.getElementById(`${watcherName}-status`);
    if (statusElement) {
        if (isRunning) {
            statusElement.classList.remove('status-stopped');
            statusElement.classList.add('status-running');
        } else {
            statusElement.classList.remove('status-running');
            statusElement.classList.add('status-stopped');
        }
    }
}

/**
 * Get watcher status
 */
async function getWatcherStatus() {
    try {
        const response = await fetch(`${API_BASE}/watchers/status`);
        const data = await response.json();
        
        if (response.ok) {
            // Update each watcher status
            Object.keys(data).forEach(watcher => {
                const isRunning = data[watcher].status === 'running';
                updateWatcherStatus(watcher, isRunning);
            });
        }
    } catch (error) {
        console.error('Failed to get watcher status:', error);
    }
}

// ============================================
// SOCIAL POSTING FUNCTIONS
// ============================================

/**
 * Post to social media platform
 */
async function postToSocial(platform) {
    const content = document.getElementById('post-content').value.trim();
    const hashtagsInput = document.getElementById('post-hashtags').value.trim();
    
    if (!content) {
        showToast('Please enter post content', 'warning');
        return;
    }
    
    // Parse hashtags
    let hashtags = [];
    if (hashtagsInput) {
        hashtags = hashtagsInput.split(/\s+/).filter(tag => tag.startsWith('#'));
    }
    
    const button = event.target.closest('button');
    const originalText = button.innerHTML;
    
    // Show loading state
    button.classList.add('btn-loading');
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Posting...';
    
    try {
        const response = await fetch(`${API_BASE}/social/post-${platform}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content,
                platform: platform,
                hashtags: hashtags
            })
        });
        
        const data = await response.json();
        
        if (response.ok || data.status === 'simulated') {
            showToast(`Posted to ${platform}!`, 'success');
            // Clear content after successful post
            document.getElementById('post-content').value = '';
            document.getElementById('post-hashtags').value = '';
            updateCharCount();
        } else {
            showToast(data.detail || 'Failed to post', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        // Reset button
        button.classList.remove('btn-loading');
        button.innerHTML = originalText;
    }
}

/**
 * Update character count
 */
function updateCharCount() {
    const content = document.getElementById('post-content').value;
    document.getElementById('char-count').textContent = `${content.length} characters`;
}

// ============================================
// AI GENERATOR FUNCTIONS
// ============================================

/**
 * Generate AI content
 */
async function generateAI(type) {
    const input = document.getElementById('ai-input').value.trim();
    const tone = document.getElementById('ai-tone').value;
    const outputDiv = document.getElementById('ai-output');
    
    if (!input) {
        showToast('Please enter input text', 'warning');
        return;
    }
    
    // Show loading state
    outputDiv.innerHTML = '<div class="flex items-center justify-center h-full"><i class="fas fa-spinner fa-spin text-purple-600 text-2xl"></i></div>';
    
    let endpoint = '';
    let body = {};
    
    switch (type) {
        case 'text':
            endpoint = 'generate-text';
            body = { prompt: input, tone: tone };
            break;
        case 'post':
            endpoint = 'generate-post';
            body = { topic: input, platform: 'linkedin', tone: tone };
            break;
        case 'reply':
            endpoint = 'generate-reply';
            body = { original_message: input, tone: tone };
            break;
    }
    
    try {
        const response = await fetch(`${API_BASE}/ai/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Display generated content
            let content = '';
            switch (type) {
                case 'text':
                    content = data.generated_text;
                    break;
                case 'post':
                    content = data.content + (data.hashtags.length ? '\n\n' + data.hashtags.join(' ') : '');
                    break;
                case 'reply':
                    content = data.reply;
                    break;
            }
            
            // Format with line breaks
            outputDiv.innerHTML = `<div class="whitespace-pre-wrap">${content.replace(/\n/g, '<br>')}</div>`;
            showToast('Content generated!', 'success');
        } else {
            outputDiv.innerHTML = `<div class="text-red-500">Error: ${data.detail || 'Generation failed'}</div>`;
            showToast('Generation failed', 'error');
        }
    } catch (error) {
        outputDiv.innerHTML = `<div class="text-red-500">Error: ${error.message}</div>`;
        showToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Copy AI output to clipboard
 */
function copyOutput() {
    const outputDiv = document.getElementById('ai-output');
    const text = outputDiv.innerText;
    
    if (text && text !== 'Generated content will appear here...') {
        copyToClipboard(text);
    } else {
        showToast('No content to copy', 'warning');
    }
}

// ============================================
// LOG VIEWER FUNCTIONS
// ============================================

/**
 * Load logs
 */
async function loadLogs() {
    const logType = document.getElementById('log-type').value;
    const logContainer = document.getElementById('log-container');
    const logCount = document.getElementById('log-count');
    
    // Show loading state
    logContainer.innerHTML = '<div class="flex items-center justify-center h-full"><i class="fas fa-spinner fa-spin text-green-600 text-2xl"></i></div>';
    
    let endpoint = '';
    switch (logType) {
        case 'whatsapp':
            endpoint = 'whatsapp-logs';
            break;
        case 'email':
            endpoint = 'email-logs';
            break;
        case 'social':
            endpoint = 'social';
            break;
        default:
            endpoint = '';
    }
    
    try {
        let data;
        if (endpoint) {
            const response = await fetch(`${API_BASE}/logs/${endpoint}`);
            data = await response.json();
        } else {
            const response = await fetch(`${API_BASE}/logs/`);
            data = await response.json();
        }
        
        if (response.ok) {
            displayLogs(data, logType);
        } else {
            logContainer.innerHTML = `<div class="text-red-500 text-center py-8">Error loading logs: ${data.detail || 'Unknown error'}</div>`;
        }
    } catch (error) {
        logContainer.innerHTML = `<div class="text-red-500 text-center py-8">Error: ${error.message}<br>Make sure the backend is running</div>`;
    }
}

/**
 * Display logs in container
 */
function displayLogs(data, logType) {
    const logContainer = document.getElementById('log-container');
    const logCount = document.getElementById('log-count');
    
    let html = '';
    let entryCount = 0;
    
    if (logType === 'whatsapp' || logType === 'email') {
        // Display WhatsApp or Email logs
        const logs = data.content?.logs || [];
        if (logs.length === 0) {
            html = '<div class="text-gray-500 text-center py-8">No logs found</div>';
        } else {
            logs.forEach(log => {
                html += `
                    <div class="mb-4 pb-4 border-b border-gray-700 last:border-0">
                        <div class="text-green-400 font-semibold mb-1">
                            <i class="fas fa-file mr-2"></i>${log.file}
                        </div>
                        <pre class="text-gray-300 text-xs overflow-x-auto whitespace-pre-wrap">${JSON.stringify(log.data, null, 2)}</pre>
                    </div>
                `;
                entryCount++;
            });
        }
    } else if (logType === 'social') {
        // Display social logs
        const posts = data.content?.posts || data.posts || [];
        if (posts.length === 0) {
            html = '<div class="text-gray-500 text-center py-8">No social posts found</div>';
        } else {
            posts.forEach((post, index) => {
                html += `
                    <div class="mb-3 pb-3 border-b border-gray-700 last:border-0">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-blue-400 font-semibold">${post.platform || 'Unknown'}</span>
                            <span class="text-gray-500 text-xs">${formatTimestamp(post.timestamp)}</span>
                        </div>
                        <div class="text-gray-300 text-sm">${post.content || JSON.stringify(post)}</div>
                    </div>
                `;
                entryCount++;
            });
        }
    } else {
        // Display all logs list
        const files = data.files || [];
        if (files.length === 0) {
            html = '<div class="text-gray-500 text-center py-8">No log files found</div>';
        } else {
            html = '<div class="space-y-2">';
            files.forEach(file => {
                html += `
                    <div class="bg-gray-800 rounded p-3 hover:bg-gray-700 cursor-pointer transition-colors" onclick="loadLogFile('${file.filename}')">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center">
                                <i class="fas fa-file-code text-green-400 mr-3"></i>
                                <span class="text-gray-200 font-mono text-sm">${file.filename}</span>
                            </div>
                            <div class="text-gray-500 text-xs">
                                ${formatBytes(file.size)} • ${file.entries || 0} entries
                            </div>
                        </div>
                    </div>
                `;
                entryCount++;
            });
            html += '</div>';
        }
    }
    
    logContainer.innerHTML = html;
    logCount.textContent = `${entryCount} entries`;
}

/**
 * Load specific log file
 */
async function loadLogFile(filename) {
    const logContainer = document.getElementById('log-container');
    
    logContainer.innerHTML = '<div class="flex items-center justify-center h-full"><i class="fas fa-spinner fa-spin text-green-600 text-2xl"></i></div>';
    
    try {
        const response = await fetch(`${API_BASE}/logs/${filename}`);
        const data = await response.json();
        
        if (response.ok) {
            let content = data.content;
            
            if (typeof content === 'object') {
                content = JSON.stringify(content, null, 2);
            }
            
            logContainer.innerHTML = `
                <div class="flex items-center justify-between mb-4">
                    <span class="text-green-400 font-semibold">
                        <i class="fas fa-file mr-2"></i>${filename}
                    </span>
                    <button onclick="loadLogs()" class="text-gray-400 hover:text-white text-sm">
                        <i class="fas fa-arrow-left mr-1"></i>Back
                    </button>
                </div>
                <pre class="text-gray-300 whitespace-pre-wrap break-all">${content}</pre>
            `;
        } else {
            logContainer.innerHTML = `<div class="text-red-500 text-center py-8">Error: ${data.detail}</div>`;
        }
    } catch (error) {
        logContainer.innerHTML = `<div class="text-red-500 text-center py-8">Error: ${error.message}</div>`;
    }
}

/**
 * Clear logs
 */
async function clearLogs() {
    if (!confirm('Are you sure you want to clear all logs? This cannot be undone.')) return;
    
    try {
        const response = await fetch(`${API_BASE}/logs/clear`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(`Cleared ${data.deleted?.length || 0} log files`, 'success');
            loadLogs();
        } else {
            showToast(data.detail || 'Failed to clear logs', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Format bytes
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// ============================================
// GENERAL FUNCTIONS
// ============================================

/**
 * Refresh all data
 */
async function refreshAll() {
    showToast('Refreshing...', 'info');
    await Promise.all([
        getWatcherStatus(),
        loadLogs()
    ]);
    showToast('Refreshed!', 'success');
}

/**
 * Smooth scroll to section
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize dark mode
    initDarkMode();
    
    // Check API connection
    checkConnection();

    // Get initial watcher status
    getWatcherStatus();

    // Load initial logs
    loadLogs();
    
    // Load WhatsApp messages
    loadWhatsAppMessages();
    
    // Load sent emails
    loadSentEmails();
    
    // Load Instagram DMs
    loadInstagramDMs();

    // Set up character count listener
    document.getElementById('post-content').addEventListener('input', updateCharCount);

    // Auto-refresh every 30 seconds
    setInterval(() => {
        checkConnection();
        getWatcherStatus();
        loadWhatsAppMessages();
        loadSentEmails();
        loadInstagramDMs();
    }, 30000);
});
