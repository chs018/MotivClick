/**
 * motivClick - Reminders Module
 * Handles reminder-related functionality
 */

/**
 * Display reminder notifications based on user settings
 */
function checkReminders() {
    // This is a placeholder for future reminder functionality
    // In a production app, this would check the user's reminder settings
    // and display notifications at the appropriate times
    
    console.log('Checking reminders...');
    
    // For now, this just logs to console
    // Future implementation could include:
    // - Web Push Notifications
    // - Email reminders via backend
    // - In-app notification badges
}

/**
 * Request notification permission from the browser
 */
async function requestNotificationPermission() {
    if (!('Notification' in window)) {
        console.log('This browser does not support notifications');
        return false;
    }
    
    if (Notification.permission === 'granted') {
        return true;
    }
    
    if (Notification.permission !== 'denied') {
        const permission = await Notification.requestPermission();
        return permission === 'granted';
    }
    
    return false;
}

/**
 * Show a browser notification
 */
function showNotification(title, options = {}) {
    if (Notification.permission === 'granted') {
        const notification = new Notification(title, {
            icon: '/static/img/icon.png',
            badge: '/static/img/badge.png',
            ...options
        });
        
        notification.onclick = function() {
            window.focus();
            notification.close();
        };
        
        return notification;
    } else {
        console.log('Notification permission not granted');
        return null;
    }
}

/**
 * Schedule a reminder for a specific time
 */
function scheduleReminder(time, message) {
    // This would use the Web Push API or a service worker in production
    console.log(`Reminder scheduled for ${time}: ${message}`);
    
    // Placeholder implementation
    // In production, you would:
    // 1. Register a service worker
    // 2. Use the Push API to schedule notifications
    // 3. Handle notifications in the background
}

/**
 * Get reminder time based on preference
 */
function getReminderTime(preference) {
    const now = new Date();
    let reminderTime = new Date();
    
    switch (preference) {
        case 'morning':
            reminderTime.setHours(9, 0, 0, 0);
            break;
        case 'afternoon':
            reminderTime.setHours(13, 0, 0, 0);
            break;
        case 'evening':
            reminderTime.setHours(19, 0, 0, 0);
            break;
        default:
            reminderTime.setHours(9, 0, 0, 0);
    }
    
    // If the time has passed today, schedule for tomorrow
    if (reminderTime < now) {
        reminderTime.setDate(reminderTime.getDate() + 1);
    }
    
    return reminderTime;
}

/**
 * Display reminder settings info
 */
function displayReminderInfo() {
    const reminderInfo = document.getElementById('reminder-info');
    
    if (!reminderInfo) return;
    
    if (Notification.permission === 'granted') {
        reminderInfo.innerHTML = `
            <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                <i class="fas fa-check-circle text-green-600 mr-2"></i>
                <span class="text-green-800">Browser notifications enabled</span>
            </div>
        `;
    } else if (Notification.permission === 'denied') {
        reminderInfo.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <i class="fas fa-times-circle text-red-600 mr-2"></i>
                <span class="text-red-800">
                    Browser notifications blocked. Please enable them in your browser settings.
                </span>
            </div>
        `;
    } else {
        reminderInfo.innerHTML = `
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <i class="fas fa-exclamation-triangle text-yellow-600 mr-2"></i>
                <span class="text-yellow-800">
                    Browser notifications not enabled.
                    <button onclick="enableNotifications()" 
                            class="ml-2 underline font-medium hover:text-yellow-900">
                        Enable now
                    </button>
                </span>
            </div>
        `;
    }
}

/**
 * Enable notifications with user interaction
 */
async function enableNotifications() {
    const granted = await requestNotificationPermission();
    
    if (granted) {
        if (window.MotivaTrack && window.MotivaTrack.showToast) {
            window.MotivaTrack.showToast('Notifications enabled!', 'success');
        }
        
        // Show a test notification
        showNotification('motivClick', {
            body: 'You will now receive reminders for your habits!',
            tag: 'welcome'
        });
        
        displayReminderInfo();
    } else {
        if (window.MotivaTrack && window.MotivaTrack.showToast) {
            window.MotivaTrack.showToast(
                'Notification permission denied',
                'warning'
            );
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Display reminder info if on settings page
    displayReminderInfo();
    
    // Check for reminders periodically (every 5 minutes)
    setInterval(checkReminders, 5 * 60 * 1000);
});

// Export for global use
window.Reminders = {
    requestNotificationPermission,
    showNotification,
    scheduleReminder,
    getReminderTime,
    displayReminderInfo,
    enableNotifications
};

window.enableNotifications = enableNotifications;
