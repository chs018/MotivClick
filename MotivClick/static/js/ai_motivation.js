/**
 * MotivaTrack - AI Motivation Module
 * Handles AI-powered motivation generation and display
 */

document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-ai-btn');
    const loadingDiv = document.getElementById('ai-loading');
    const contentDiv = document.getElementById('ai-content');
    
    if (generateBtn) {
        generateBtn.addEventListener('click', async function() {
            // Disable button and show loading
            generateBtn.disabled = true;
            generateBtn.classList.add('opacity-50', 'cursor-not-allowed');
            
            if (loadingDiv) {
                loadingDiv.classList.remove('hidden');
            }
            
            try {
                const response = await fetch('/ai/motivation/today', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const result = await response.json();
                
                if (result.success && result.data) {
                    displayMotivation(result.data);
                    
                    // Hide button and loading, show content
                    generateBtn.classList.add('hidden');
                    if (loadingDiv) {
                        loadingDiv.classList.add('hidden');
                    }
                    if (contentDiv) {
                        contentDiv.classList.remove('hidden');
                    }
                } else {
                    throw new Error(result.error || 'Failed to generate motivation');
                }
            } catch (error) {
                console.error('Error generating AI motivation:', error);
                
                if (loadingDiv) {
                    loadingDiv.classList.add('hidden');
                }
                
                // Show error message
                if (window.MotivaTrack && window.MotivaTrack.showToast) {
                    window.MotivaTrack.showToast(
                        'Error generating motivation. Please try again.',
                        'error'
                    );
                } else {
                    alert('Error generating motivation. Please try again.');
                }
                
                // Re-enable button
                generateBtn.disabled = false;
                generateBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        });
    }
});

/**
 * Display AI-generated motivation content
 */
function displayMotivation(data) {
    const contentDiv = document.getElementById('ai-content');
    
    if (!contentDiv) {
        console.error('AI content div not found');
        return;
    }
    
    // Build HTML for the motivation display
    let html = '';
    
    // Summary
    if (data.summary) {
        html += `
            <p class="text-indigo-100 mb-4">
                <i class="fas fa-chart-line mr-2"></i>${data.summary}
            </p>
        `;
    }
    
    // Suggestions
    if (data.suggestions && data.suggestions.length > 0) {
        html += `
            <div class="bg-white/10 rounded-lg p-4 backdrop-blur-sm mb-4">
                <h3 class="font-semibold mb-3 flex items-center">
                    <i class="fas fa-lightbulb mr-2"></i>Your personalized tips:
                </h3>
                <ul class="space-y-2 text-sm">
        `;
        
        data.suggestions.forEach((suggestion, index) => {
            html += `
                <li class="flex items-start">
                    <span class="font-bold mr-2">${index + 1}.</span>
                    <span>${escapeHtml(suggestion)}</span>
                </li>
            `;
        });
        
        html += `
                </ul>
            </div>
        `;
    }
    
    // Motivation message
    if (data.motivation) {
        html += `
            <div class="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                <div class="flex items-start">
                    <i class="fas fa-quote-left text-2xl mr-3 mt-1 opacity-70"></i>
                    <p class="italic flex-1">${escapeHtml(data.motivation)}</p>
                    <i class="fas fa-quote-right text-2xl ml-3 mt-1 opacity-70"></i>
                </div>
            </div>
        `;
    }
    
    // Add a refresh button
    html += `
        <div class="mt-4 text-center">
            <button onclick="refreshMotivation()" 
                    class="text-white/80 hover:text-white text-sm underline">
                <i class="fas fa-sync-alt mr-1"></i>Regenerate motivation
            </button>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

/**
 * Refresh motivation (regenerate)
 */
async function refreshMotivation() {
    const contentDiv = document.getElementById('ai-content');
    
    if (!contentDiv) return;
    
    // Show loading state
    contentDiv.innerHTML = `
        <div class="text-center py-8">
            <i class="fas fa-spinner fa-spin text-4xl mb-4"></i>
            <p>Generating fresh motivation...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/ai/motivation/today', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success && result.data) {
            displayMotivation(result.data);
            
            if (window.MotivaTrack && window.MotivaTrack.showToast) {
                window.MotivaTrack.showToast('Motivation refreshed! ✨', 'success');
            }
        } else {
            throw new Error(result.error || 'Failed to generate motivation');
        }
    } catch (error) {
        console.error('Error refreshing motivation:', error);
        
        contentDiv.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-triangle text-4xl text-red-300 mb-4"></i>
                <p class="mb-4">Failed to refresh motivation</p>
                <button onclick="refreshMotivation()" 
                        class="bg-white text-indigo-600 hover:bg-indigo-50 font-semibold py-2 px-6 rounded-lg">
                    Try Again
                </button>
            </div>
        `;
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export for global use
window.refreshMotivation = refreshMotivation;
