/**
 * MotivaTrack - Main JavaScript
 * Handles habit logging and general UI interactions
 */

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
});

// Habit checkbox handling
document.addEventListener('DOMContentLoaded', function() {
    const habitCheckboxes = document.querySelectorAll('.habit-checkbox');
    
    habitCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', async function() {
            const habitId = this.dataset.habitId;
            const isChecked = this.checked;
            const status = isChecked ? 'completed' : 'skipped';
            
            // Get today's date in ISO format
            const today = new Date().toISOString().split('T')[0];
            
            try {
                const response = await fetch('/habits/log', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        habit_id: habitId,
                        date: today,
                        status: status
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Update streak display
                    const streakElement = document.querySelector(`.habit-streak[data-habit-id="${habitId}"]`);
                    if (streakElement) {
                        streakElement.textContent = data.streak;
                        
                        // Add a brief animation
                        streakElement.classList.add('animate-pulse');
                        setTimeout(() => {
                            streakElement.classList.remove('animate-pulse');
                        }, 1000);
                    }
                    
                    // Show success feedback
                    showToast(
                        isChecked ? 'Habit completed! 🎉' : 'Habit unchecked',
                        'success'
                    );
                } else {
                    throw new Error(data.error || 'Failed to log habit');
                }
            } catch (error) {
                console.error('Error logging habit:', error);
                // Revert checkbox state
                this.checked = !isChecked;
                showToast('Error logging habit. Please try again.', 'error');
            }
        });
    });
});

// Toast notification system
function showToast(message, type = 'info') {
    // Remove any existing toasts
    const existingToast = document.getElementById('toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.id = 'toast-notification';
    toast.className = `fixed bottom-4 right-4 z-50 max-w-sm rounded-lg shadow-lg p-4 transition-all duration-300 transform translate-y-0 opacity-100`;
    
    // Set colors based on type
    let bgColor, textColor, icon;
    switch (type) {
        case 'success':
            bgColor = 'bg-green-500';
            textColor = 'text-white';
            icon = 'fa-check-circle';
            break;
        case 'error':
            bgColor = 'bg-red-500';
            textColor = 'text-white';
            icon = 'fa-exclamation-circle';
            break;
        case 'warning':
            bgColor = 'bg-yellow-500';
            textColor = 'text-white';
            icon = 'fa-exclamation-triangle';
            break;
        default:
            bgColor = 'bg-blue-500';
            textColor = 'text-white';
            icon = 'fa-info-circle';
    }
    
    toast.className += ` ${bgColor} ${textColor}`;
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${icon} mr-3 text-xl"></i>
            <span class="font-medium">${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('translate-y-full', 'opacity-0');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

// Date formatting helper
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Confirm delete actions
document.addEventListener('DOMContentLoaded', function() {
    const deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const message = this.getAttribute('onsubmit').match(/'([^']+)'/)[1];
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});

// Export for use in other modules
window.MotivaTrack = {
    showToast,
    validateEmail,
    validatePassword,
    formatDate
};
