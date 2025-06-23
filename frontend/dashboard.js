// Configuration
const API_URL = 'http://localhost:8002';

// Global state for selected career paths (MVP approach)
let selectedCareerPaths = [];

// Validation Constants
const VALIDATION_RULES = {
    linkedin: {
        minLength: 20,
        pattern: /^https:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9-]+\/?$/,
        message: 'Please enter a valid LinkedIn profile URL (e.g., https://linkedin.com/in/username)'
    },
    story: {
        minWords: 50,
        maxWords: 5000,
        message: 'Personal story should be between 50 and 5000 words'
    },
    resume: {
        minWords: 100,
        maxWords: 2000,
        message: 'Resume should be between 100 and 2000 words'
    }
};

// Validation Functions
function validateLinkedIn(url) {
    if (!url) return 'LinkedIn URL is required';
    if (!VALIDATION_RULES.linkedin.pattern.test(url)) {
        return VALIDATION_RULES.linkedin.message;
    }
    return null;
}

function validateStory(story) {
    if (!story) return 'Personal story is required';
    const words = story.trim().split(/\s+/).length;
    if (words < VALIDATION_RULES.story.minWords) {
        return `Personal story is too short (minimum ${VALIDATION_RULES.story.minWords} words)`;
    }
    if (words > VALIDATION_RULES.story.maxWords) {
        return `Personal story is too long (maximum ${VALIDATION_RULES.story.maxWords} words)`;
    }
    return null;
}

function validateResume(resume) {
    if (!resume) return 'Resume is required';
    const words = resume.trim().split(/\s+/).length;
    if (words < VALIDATION_RULES.resume.minWords) {
        return `Resume is too short (minimum ${VALIDATION_RULES.resume.minWords} words)`;
    }
    if (words > VALIDATION_RULES.resume.maxWords) {
        return `Resume is too long (maximum ${VALIDATION_RULES.resume.maxWords} words)`;
    }
    return null;
}

// UI Feedback Functions
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorDiv = document.getElementById(`${fieldId}-error`) || createErrorDiv(fieldId);
    
    field.classList.add('border-red-500');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function clearFieldError(fieldId) {
    const field = document.getElementById(fieldId);
    const errorDiv = document.getElementById(`${fieldId}-error`);
    
    if (field) field.classList.remove('border-red-500');
    if (errorDiv) errorDiv.classList.add('hidden');
}

function createErrorDiv(fieldId) {
    const field = document.getElementById(fieldId);
    const errorDiv = document.createElement('div');
    errorDiv.id = `${fieldId}-error`;
    errorDiv.className = 'text-red-500 text-sm mt-1';
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
    return errorDiv;
}

// API Client Functions
async function validateAndAnalyzeCareer(linkedinUrl, personalStory, sampleResume) {
    // Validate all inputs first
    const linkedinError = validateLinkedIn(linkedinUrl);
    const storyError = validateStory(personalStory);
    const resumeError = validateResume(sampleResume);

    // Clear previous errors
    clearFieldError('linkedin_profile');
    clearFieldError('personal_story');
    clearFieldError('sample_resume');

    // Show any validation errors
    if (linkedinError) showFieldError('linkedin_profile', linkedinError);
    if (storyError) showFieldError('personal_story', storyError);
    if (resumeError) showFieldError('sample_resume', resumeError);

    // If any validation failed, don't proceed
    if (linkedinError || storyError || resumeError) {
        return null;
    }

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
            const errorData = await response.json();
            throw new Error(errorData.detail || `API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error analyzing career:', error);
        throw error;
    }
}

// Real-time validation
function setupRealTimeValidation() {
    const linkedinField = document.getElementById('linkedin_profile');
    const storyField = document.getElementById('personal_story');
    const resumeField = document.getElementById('sample_resume');

    linkedinField.addEventListener('blur', () => {
        const error = validateLinkedIn(linkedinField.value);
        if (error) {
            showFieldError('linkedin_profile', error);
        } else {
            clearFieldError('linkedin_profile');
        }
    });

    storyField.addEventListener('input', debounce(() => {
        const error = validateStory(storyField.value);
        if (error) {
            showFieldError('personal_story', error);
        } else {
            clearFieldError('personal_story');
        }
    }, 500));

    resumeField.addEventListener('input', debounce(() => {
        const error = validateResume(resumeField.value);
        if (error) {
            showFieldError('sample_resume', error);
        } else {
            clearFieldError('sample_resume');
        }
    }, 500));
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Enhanced UI Update Functions
function showLoading() {
    const placeholder = document.getElementById('placeholder');
    const analysisResults = document.getElementById('analysis-results');
    
    // Clear any previous errors
    clearFieldError('linkedin_profile');
    clearFieldError('personal_story');
    clearFieldError('sample_resume');
    
    placeholder.classList.remove('hidden');
    analysisResults.classList.add('hidden');
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.textContent = 'Analyzing...';
    analyzeBtn.disabled = true;
    
    // Add loading animation
    placeholder.innerHTML = `
        <div class="animate-pulse flex flex-col items-center">
            <div class="rounded-full bg-gray-200 h-12 w-12 mb-4"></div>
            <div class="h-4 bg-gray-200 rounded w-24 mb-2"></div>
            <div class="h-3 bg-gray-200 rounded w-32"></div>
        </div>
    `;
}

function hideLoading() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.textContent = 'Analyze My Career';
    analyzeBtn.disabled = false;
}

function showError(message) {
    alert(message); // You might want to replace this with a better error UI
}

function showRefineLoading() {
    const refineBtn = document.getElementById('refineBtn');
    const refineBtnText = document.getElementById('refineBtn-text');
    const refineBtnSpinner = document.getElementById('refineBtn-spinner');
    
    refineBtn.disabled = true;
    refineBtnText.classList.add('hidden');
    refineBtnSpinner.classList.remove('hidden');
}

function hideRefineLoading() {
    const refineBtn = document.getElementById('refineBtn');
    const refineBtnText = document.getElementById('refineBtn-text');
    const refineBtnSpinner = document.getElementById('refineBtn-spinner');
    
    refineBtn.disabled = false;
    refineBtnText.classList.remove('hidden');
    refineBtnSpinner.classList.add('hidden');
}

function displayCareerPaths(newCareerPaths, append = false, refined = false) {
    const careerPathsContainer = document.getElementById('career-paths');
    if (!append) {
        careerPathsContainer.innerHTML = ''; // Clear existing paths if not appending
    }

    // Get existing paths titles to avoid duplicates
    const existingTitles = new Set();
    const existingCheckboxes = document.querySelectorAll('.career-path-checkbox');
    existingCheckboxes.forEach(cb => {
        existingTitles.add(cb.dataset.path);
    });

    newCareerPaths.forEach((path, index) => {
        if (existingTitles.has(path.title)) {
            return; // Skip duplicates
        }
        const label = document.createElement('label');
        label.className = 'flex flex-col p-4 rounded-lg border border-gray-200 cursor-pointer transition-colors ' + 
            (refined ? 'bg-yellow-50 hover:bg-yellow-100 border-yellow-300' : 'bg-gray-100 hover:bg-indigo-50');

        label.innerHTML = `
            <div class="flex justify-between items-center">
                <div class="flex items-center">
                    <input type="checkbox" class="career-path-checkbox mt-1 mr-3 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded" 
                           data-path="${path.title}" 
                           data-keywords="${path.keywords.join(', ')}"
                           data-strengths="${path.strengths || ''}"
                           data-index="${index}">
                    <p class="font-semibold text-gray-800 mb-0">${path.title} ${refined ? '<span class="ml-2 inline-block bg-yellow-300 text-yellow-900 text-xs font-semibold px-2 py-0.5 rounded">Refined</span>' : ''}</p>
                </div>
                <button type="button" class="toggle-details text-indigo-600 font-bold focus:outline-none" aria-expanded="true" aria-label="Toggle details for ' + path.title + '">−</button>
            </div>
            <div class="career-path-details mt-2">
                <p class="text-sm text-gray-600">${path.strengths || ''}</p>
                <p class="text-xs text-gray-500 mt-2">Keywords: ${path.keywords.join(', ')}</p>
            </div>
        `;

        careerPathsContainer.appendChild(label);
    });

    // Set up event listeners for checkboxes
    setupCareerPathSelection();

    // Set up toggle buttons for collapsible details
    const toggleButtons = careerPathsContainer.querySelectorAll('.toggle-details');
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const label = button.closest('label');
            const details = label.querySelector('.career-path-details');
            const expanded = button.getAttribute('aria-expanded') === 'true';

            if (expanded) {
                details.classList.add('hidden');
                button.textContent = '+';
                button.setAttribute('aria-expanded', 'false');
            } else {
                details.classList.remove('hidden');
                button.textContent = '−';
                button.setAttribute('aria-expanded', 'true');
            }
        });
    });
}

// MVP Multi-path selection logic
function setupCareerPathSelection() {
    const checkboxes = document.querySelectorAll('.career-path-checkbox');
    const continueBtn = document.getElementById('continueWithSelectionBtn');
    const selectionSummary = document.getElementById('selection-summary');
    const selectedPathsList = document.getElementById('selected-paths-list');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            updateSelectedPaths();
        });
    });

    continueBtn.addEventListener('click', () => {
        if (selectedCareerPaths.length > 0) {
            showConfirmationSection();
        }
    });

    function updateSelectedPaths() {
        selectedCareerPaths = [];
        const checkedBoxes = document.querySelectorAll('.career-path-checkbox:checked');
        
        checkedBoxes.forEach(checkbox => {
            selectedCareerPaths.push({
                title: checkbox.dataset.path,
                keywords: checkbox.dataset.keywords.split(', '),
                strengths: checkbox.dataset.strengths
            });
        });

        // Update UI based on selection
        if (selectedCareerPaths.length > 0) {
            continueBtn.disabled = false;
            selectionSummary.classList.remove('hidden');
            selectedPathsList.innerHTML = selectedCareerPaths.map(path => 
                `<span class="inline-block bg-white px-2 py-1 rounded text-xs mr-2 mb-1">${path.title}</span>`
            ).join('');
        } else {
            continueBtn.disabled = true;
            selectionSummary.classList.add('hidden');
        }
    }
}

function showConfirmationSection() {
    const confirmationSection = document.getElementById('ai-confirmation-section');
    const confirmationText = document.querySelector('#ai-confirmation-section p');
    
    // Generate confirmation text for multiple paths
    let pathText;
    if (selectedCareerPaths.length === 1) {
        pathText = `<strong>${selectedCareerPaths[0].title}</strong> roles`;
    } else if (selectedCareerPaths.length === 2) {
        pathText = `<strong>${selectedCareerPaths[0].title}</strong> and <strong>${selectedCareerPaths[1].title}</strong> roles`;
    } else {
        const lastPath = selectedCareerPaths[selectedCareerPaths.length - 1];
        const otherPaths = selectedCareerPaths.slice(0, -1);
        pathText = `<strong>${otherPaths.map(p => p.title).join('</strong>, <strong>')}</strong>, and <strong>${lastPath.title}</strong> roles`;
    }
    
    confirmationText.innerHTML = `New plan: We are targeting ${pathText}. I will now tailor your resume and search for matching jobs across these career paths.`;
    confirmationSection.classList.remove('hidden');
}

// Enhanced Event Handlers
console.log('DOM fully loaded and parsed');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired');
    // Set up real-time validation
    setupRealTimeValidation();
    const analyzeBtn = document.getElementById('analyzeBtn');
    const placeholder = document.getElementById('placeholder');
    const analysisResults = document.getElementById('analysis-results');

    analyzeBtn.addEventListener('click', async () => {
        // Get user input
        const linkedin = document.getElementById('linkedin_profile').value.trim();
        const story = document.getElementById('personal_story').value.trim();
        const resume = document.getElementById('sample_resume').value.trim();

        try {
            showLoading();
            
            // Mock data for testing
            const mockCareerPaths = {
                careerPaths: [
                    {
                        title: "Technical Project Manager",
                        strengths: "Strong leadership and technical background",
                        keywords: ["Agile", "Team Leadership", "Scrum", "MERN Stack"]
                    },
                    {
                        title: "Senior Front-End Engineer",
                        strengths: "Deep expertise in modern web technologies",
                        keywords: ["React", "TypeScript", "Performance", "CI/CD"]
                    },
                    {
                        title: "Full-Stack Developer",
                        strengths: "Versatile across frontend and backend",
                        keywords: ["JavaScript", "Node.js", "Database Design", "API Development"]
                    },
                    {
                        title: "DevOps Engineer",
                        strengths: "Infrastructure and automation expertise",
                        keywords: ["Docker", "Kubernetes", "AWS", "CI/CD Pipelines"]
                    }
                ]
            };

            // Validate and call the AI Copilot Service
            let result;
            try {
                result = await validateAndAnalyzeCareer(linkedin, story, resume);
            } catch (error) {
                // Fallback to mock data for MVP testing when backend is not available
                console.log('Backend not available, using mock data for MVP testing');
                result = mockCareerPaths;
            }
            
            // If validation failed but we want to test with mock data anyway
            if (!result) {
                console.log('Validation failed, using mock data for testing purposes');
                result = mockCareerPaths;
            }
            
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

    // Initialize other button handlers with multi-path support
    const findJobsBtn = document.getElementById('findJobsBtn');
    findJobsBtn.addEventListener('click', () => {
        if (selectedCareerPaths.length > 0) {
            const pathNames = selectedCareerPaths.map(p => p.title).join(', ');
            alert(`Triggering job scraper service for: ${pathNames}`);
            // TODO: Implement job scraping integration with multiple paths
        } else {
            alert('Please select career paths first.');
        }
    });
    
    const generateResumeBtn = document.getElementById('generateResumeBtn');
    generateResumeBtn.addEventListener('click', () => {
        if (selectedCareerPaths.length > 0) {
            const pathNames = selectedCareerPaths.map(p => p.title).join(', ');
            alert(`Generating tailored resume for: ${pathNames}`);
            // TODO: Implement resume generation with multiple paths
        } else {
            alert('Please select career paths first.');
        }
    });

    // Refinement button handler - using correct ID from HTML
    const refineBtn = document.getElementById('refineBtn');
    const refinementInput = document.getElementById('refinementText'); // This matches the HTML

    console.log('refineBtn:', refineBtn);
    console.log('refinementInput:', refinementInput);
    
    refineBtn.addEventListener('click', async () => {
        console.log('refineBtn clicked');
        const refinementText = refinementInput.value.trim();
        
        if (!refinementText) {
            showError('Please enter your refinement preferences.');
            return;
        }

        if (selectedCareerPaths.length === 0) {
            showError('Please select at least one career path first.');
            return;
        }

        try {
            showRefineLoading();
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

            const response = await fetch(`${API_URL}/refine-strategy`, {
                signal: controller.signal,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    linkedin_url: document.getElementById('linkedin_profile').value.trim(),
                    personal_story: document.getElementById('personal_story').value.trim(),
                    sample_resume: document.getElementById('sample_resume').value.trim(),
                    selected_paths: selectedCareerPaths.map(path => path.title),
                    refinement_text: refinementText
                })
            });

            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `API Error: ${response.status}`);
            }

            const result = await response.json();
            
            // Display the new career paths, appending to existing ones
            if (result.refinedPaths && result.refinedPaths.length > 0) {
                // Append new paths instead of replacing, mark as refined
                displayCareerPaths(result.refinedPaths, true, true);
                
                // Update the confirmation text
                const confirmationText = document.querySelector('#ai-confirmation-section p');
                confirmationText.innerHTML = 'Based on your refinement, here are additional career paths that match your entrepreneurial background. Select any that interest you.';
                
                // Clear the refinement input
                refinementInput.value = '';
                
                // Show the confirmation section
                document.getElementById('ai-confirmation-section').classList.remove('hidden');
            } else {
                showError('No additional career paths found. Please try different refinement criteria.');
            }

        } catch (error) {
            console.error('Error refining strategy:', error);
            clearTimeout(timeoutId); // Clean up timeout
            // Fallback for MVP testing when backend is not available
            const confirmationText = document.querySelector('#ai-confirmation-section p');
            confirmationText.innerHTML = `Refined plan: Focusing on ${selectedCareerPaths.map(p => `<strong>${p.title}</strong>`).join(' and ')} with emphasis on ${refinementText}`;
            refinementInput.value = '';
            document.getElementById('ai-confirmation-section').classList.remove('hidden');
        } finally {
            hideRefineLoading();
        }
    });
});
