// Configuration - Use same origin for API calls
const API_BASE_URL = window.location.origin;

// DOM Elements
const matchForm = document.getElementById('matchForm');
const resultsSection = document.getElementById('resultsSection');
const loadingSection = document.getElementById('loadingSection');
const errorSection = document.getElementById('errorSection');
const resultsInfo = document.getElementById('resultsInfo');
const resultsGrid = document.getElementById('results');
const errorMessage = document.getElementById('errorMessage');
const healthStatus = document.getElementById('healthStatus');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');

// Check health on load
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        updateHealthStatus(data);
    } catch (error) {
        updateHealthStatus({
            status: 'error',
            error: 'Cannot connect to server'
        });
    }
}

function updateHealthStatus(data) {
    const status = data.status || 'error';
    
    statusIndicator.className = `status-indicator ${status}`;
    
    if (status === 'ok') {
        statusText.textContent = '✓ System is healthy';
    } else if (status === 'degraded') {
        const issues = [];
        if (data.checks) {
            if (data.checks.database !== 'ok') issues.push('database');
            if (data.checks.openai === 'not_configured') issues.push('OpenAI');
        }
        statusText.textContent = `⚠ System degraded: ${issues.join(', ')} issues`;
    } else {
        statusText.textContent = `✗ System error: ${data.error || 'Unknown error'}`;
    }
}

// Handle form submission
matchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(matchForm);
    const tags = formData.get('tags');
    const topN = parseInt(formData.get('topN'));
    const minSimilarity = parseFloat(formData.get('minSimilarity'));
    const onlySuccessful = formData.get('onlySuccessful') === 'on';
    const artistName = formData.get('artistName');
    const persistArtist = formData.get('persistArtist') === 'on';
    
    // Validate
    if (!tags.trim()) {
        showError('Please enter some tags');
        return;
    }
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/match`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tags: tags.trim(),
                top_n: topN,
                min_similarity: minSimilarity,
                only_successful: onlySuccessful,
                artist_name: artistName.trim() || null,
                persist_artist: persistArtist && artistName.trim()
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to fetch matches');
        }
        
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error fetching matches:', error);
        showError(error.message || 'Failed to fetch matches. Please try again.');
    }
});

function showLoading() {
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    loadingSection.style.display = 'block';
}

function showError(message) {
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'block';
    errorMessage.textContent = message;
}

function displayResults(data) {
    loadingSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    if (!data.matches || data.matches.length === 0) {
        showError('No matches found. Try adjusting your tags or lowering the minimum similarity.');
        return;
    }
    
    // Display info
    resultsInfo.innerHTML = `
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
            <div>
                <strong>Your Tags:</strong> ${data.user_tags}
            </div>
            <div>
                <strong>Matches Found:</strong> ${data.total_matches}
            </div>
            <div>
                <strong>Parameters:</strong> 
                Top ${data.parameters.top_n}, 
                Min Similarity: ${data.parameters.min_similarity}
                ${data.parameters.only_successful ? ', Only Successful' : ''}
            </div>
        </div>
    `;
    
    // Display matches
    resultsGrid.innerHTML = data.matches.map((match, index) => {
        const scorePercent = Math.round(match.final_score * 100);
        const semanticPercent = Math.round(match.semantic_similarity * 100);
        const historicalPercent = match.historical_success_rate 
            ? Math.round(match.historical_success_rate * 100)
            : 'N/A';
        
        let recommendationClass = 'risky';
        if (match.final_score >= 0.7) recommendationClass = 'highly-recommended';
        else if (match.final_score >= 0.5) recommendationClass = 'good-match';
        
        return `
            <div class="result-card">
                <h3>${index + 1}. ${match.artist_name || 'Unknown Artist'}</h3>
                <p class="artist-tags">${match.artist_tags || 'No tags available'}</p>
                
                <div class="score-section">
                    <div class="score-item">
                        <span class="score-label">Overall Score</span>
                        <span class="score-value">${scorePercent}%</span>
                    </div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${scorePercent}%"></div>
                    </div>
                    
                    <div class="score-item">
                        <span class="score-label">Semantic Similarity</span>
                        <span class="score-value">${semanticPercent}%</span>
                    </div>
                    
                    ${match.historical_success_rate !== null && match.historical_success_rate !== undefined ? `
                    <div class="score-item">
                        <span class="score-label">Historical Success Rate</span>
                        <span class="score-value">${historicalPercent}%</span>
                    </div>
                    ` : ''}
                </div>
                
                <div class="recommendation ${recommendationClass}">
                    ${match.recommendation || 'No recommendation available'}
                </div>
            </div>
        `;
    }).join('');
    
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Initialize
checkHealth();

// Refresh health every 30 seconds
setInterval(checkHealth, 30000);
