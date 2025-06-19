// Configuration
const API_URL = 'http://localhost:8002';

// API Client Functions
async function analyzeCareer(linkedinUrl, personalStory, sampleResume) {
    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                linkedin_url: linkedinUrl,
                personal_story: personalStory,
                sample_resume: sampleResume
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error analyzing career:', error);
        throw error;
    }
}

// UI Update Functions
function showLoading() {
    const placeholder = document.getElementById('placeholder');
    const analysisResults = document.getElementById('analysis-results');
    
    placeholder.classList.remove('hidden');
    analysisResults.classList.add('hidden');
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.textContent = 'Analyzing...';
    analyzeBtn.disabled = true;
}

function hideLoading() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.textContent = 'Analyze My Career';
    analyzeBtn.disabled = false;
}

function showError(message) {
    alert(message); // You might want to replace this with a better error UI
}

function displayCareerPaths(careerPaths) {
    const careerPathsContainer = document.getElementById('career-paths');
    careerPathsContainer.innerHTML = ''; // Clear existing paths

    careerPaths.forEach(path => {
        const button = document.createElement('button');
        button.className = 'w-full text-left p-4 bg-gray-100 hover:bg-indigo-100 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500';
        button.innerHTML = `
            <p class="font-semibold text-gray-800">${path.title}</p>
            <p class="text-sm text-gray-600 mt-1">${path.strengths}</p>
            <p class="text-xs text-gray-500 mt-2">Keywords: ${path.keywords.join(', ')}</p>
        `;
        
        button.addEventListener('click', () => {
            // Show confirmation section when a path is selected
            document.getElementById('ai-confirmation-section').classList.remove('hidden');
            
            // Update the confirmation text
            const confirmationText = document.querySelector('#ai-confirmation-section p');
            confirmationText.textContent = `New plan: We are targeting **${path.title}** roles. I will now tailor your resume and search for matching jobs.`;
        });

        careerPathsContainer.appendChild(button);
    });
}

// Event Handlers
document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const placeholder = document.getElementById('placeholder');
    const analysisResults = document.getElementById('analysis-results');

    analyzeBtn.addEventListener('click', async () => {
        // Get user input
        const linkedin = document.getElementById('linkedin_profile').value;
        const story = document.getElementById('personal_story').value;
        const resume = document.getElementById('sample_resume').value;

        if (!linkedin || !story || !resume) {
            showError('Please fill out all three fields.');
            return;
        }

        try {
            showLoading();
            
            // Call the AI Copilot Service
            const result = await analyzeCareer(linkedin, story, resume);
            
            // Hide placeholder, show results
            placeholder.classList.add('hidden');
            analysisResults.classList.remove('hidden');
            
            // Display the career paths
            displayCareerPaths(result.careerPaths);
            
        } catch (error) {
            showError('Failed to analyze career. Please try again.');
            console.error(error);
        } finally {
            hideLoading();
        }
    });

    // Initialize other button handlers
    const findJobsBtn = document.getElementById('findJobsBtn');
    findJobsBtn.addEventListener('click', () => {
        // TODO: Implement job scraping integration
        alert('Triggering job scraper service with the new strategy!');
    });
    
    const generateResumeBtn = document.getElementById('generateResumeBtn');
    generateResumeBtn.addEventListener('click', () => {
        // TODO: Implement resume generation
        alert('Generating a perfectly tailored resume...');
    });
});
