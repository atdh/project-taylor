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
                <button type="button" class="toggle-details w-6 h-6 cursor-pointer rounded-full hover:bg-gray-200 text-indigo-600 font-bold focus:outline-none" aria-expanded="true" aria-label="Toggle details for ${path.title}">−</button>
            </div>
            <div class="career-path-details mt-2">
                <p class="text-[15px] leading-relaxed text-gray-600">${path.strengths || ''}</p>
                <p class="text-[15px] leading-relaxed text-gray-500 mt-2">Keywords: ${path.keywords.join(', ')}</p>
            </div>
        `;

        careerPathsContainer.appendChild(label);
    });

    // Set up event listeners for checkboxes
    setupCareerPathSelection();

    // Add subtle hover/focus feedback on card body or title section
    const labels = careerPathsContainer.querySelectorAll('label');
    labels.forEach(label => {
        label.addEventListener('mouseenter', () => {
            label.classList.add('shadow-md');
        });
        label.addEventListener('mouseleave', () => {
            label.classList.remove('shadow-md');
        });
        label.addEventListener('focusin', () => {
            label.classList.add('shadow-md');
        });
        label.addEventListener('focusout', () => {
            label.classList.remove('shadow-md');
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

// Setup event delegation for toggle buttons
function setupToggleEventDelegation() {
    const careerPathsContainer = document.getElementById('career-paths');
    
    // Remove any existing event listener to prevent duplicates
    careerPathsContainer.removeEventListener('click', handleToggleClick);
    
    // Add event delegation for toggle buttons
    careerPathsContainer.addEventListener('click', handleToggleClick);
}

function handleToggleClick(event) {
    // Check if the clicked element is a toggle button
    if (event.target.classList.contains('toggle-details')) {
        const button = event.target;
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
    }
}

// Enhanced Event Handlers
console.log('DOM fully loaded and parsed');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired');
    // Set up real-time validation
    setupRealTimeValidation();
    
    // Set up event delegation for toggle buttons
    setupToggleEventDelegation();
    
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
    findJobsBtn.addEventListener('click', async () => {
        if (selectedCareerPaths.length > 0) {
            try {
                // Show loading state
                findJobsBtn.disabled = true;
                findJobsBtn.innerHTML = '<span class="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>Searching...';
                
                // Prepare request data
                const requestData = {
                    career_paths: selectedCareerPaths.map(path => ({
                        id: path.id || Math.random().toString(36).substr(2, 9),
                        title: path.title,
                        keywords: path.keywords || []
                    })),
                    total_jobs_requested: 100,
                    location: "remote",
                    filters: {
                        experience: "senior",
                        posted_within: "7d"
                    }
                };
                
                // Prepare AI-enhanced request data
                const aiRequestData = {
                    linkedin_url: document.getElementById('linkedin_profile').value.trim(),
                    personal_story: document.getElementById('personal_story').value.trim(),
                    sample_resume: document.getElementById('sample_resume').value.trim(),
                    career_paths: selectedCareerPaths.map(path => ({
                        title: path.title,
                        keywords: Array.isArray(path.keywords) ? path.keywords : 
                                 (typeof path.keywords === 'string' ? path.keywords.split(', ') : []),
                        strengths: path.strengths || ''
                    })),
                    preferences: {
                        location: "remote",
                        experience_level: "senior",
                        company_size: "any"
                    }
                };
                
                // Call the AI-enhanced job search API
                const response = await fetch('http://localhost:8001/api/search-jobs-ai', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(aiRequestData)
                });
                
                if (!response.ok) {
                    throw new Error(`API Error: ${response.status}`);
                }
                
                const jobResults = await response.json();
                
                // Display job results
                displayJobResults(jobResults);
                
            } catch (error) {
                console.error('Error searching jobs:', error);
                // For MVP testing, use mock data
                const mockJobResults = generateMockJobResults(selectedCareerPaths);
                displayJobResults(mockJobResults);
            } finally {
                // Reset button state
                findJobsBtn.disabled = false;
                findJobsBtn.innerHTML = 'Find Relevant Jobs';
            }
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

// Function to generate mock job results for testing
function generateMockJobResults(careerPaths) {
    const allocation_summary = {};
    const jobs_by_path = {};
    let total_jobs_found = 0;
    
    // Simulate job distribution with some paths having fewer results
    careerPaths.forEach((path, index) => {
        const requested = Math.floor(100 / careerPaths.length);
        let found = requested;
        
        // Simulate some paths having fewer results
        if (path.title.toLowerCase().includes('junior') || index === 0) {
            found = Math.floor(requested * 0.3); // Only 30% found
        } else if (index === careerPaths.length - 1) {
            found = requested + 20; // This path has more results
        }
        
        allocation_summary[path.title] = {
            requested: requested,
            found: found
        };
        
        // Generate mock jobs for this path
        const jobs = [];
        for (let i = 0; i < found; i++) {
            jobs.push({
                title: `${path.title} - Position ${i + 1}`,
                company: `Company ${Math.floor(Math.random() * 50) + 1}`,
                location: "Remote",
                description: `Exciting opportunity for a ${path.title} with experience in ${path.keywords ? path.keywords.join(', ') : 'various technologies'}.`,
                url: `https://example.com/jobs/${path.title.toLowerCase().replace(/\s+/g, '-')}-${i + 1}`,
                posted_date: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                salary_range: {
                    min: 80000 + (Math.floor(Math.random() * 8) * 10000),
                    max: 150000 + (Math.floor(Math.random() * 10) * 10000),
                    currency: "USD"
                }
            });
        }
        
        jobs_by_path[path.title] = jobs;
        total_jobs_found += found;
    });
    
    return {
        allocation_summary,
        jobs_by_path,
        total_jobs_found,
        search_metadata: {
            search_strategy: "smart_distribution",
            deduplication: "first_path",
            paths_searched: careerPaths.length
        }
    };
}

// Function to display job results
function displayJobResults(jobResults) {
    // Hide the career paths section and show job results
    const careerPathsSection = document.getElementById('career-paths-section');
    const aiConfirmationSection = document.getElementById('ai-confirmation-section');
    
    // Create job results container
    const jobResultsHTML = `
        <div id="job-results-section" class="mt-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Job Search Results</h3>
            
            <!-- Allocation Summary -->
            <div class="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 class="font-medium text-blue-900 mb-2">Job Allocation Summary</h4>
                <div class="space-y-2">
                    ${Object.entries(jobResults.allocation_summary).map(([path, stats]) => `
                        <div class="flex justify-between text-sm">
                            <span class="text-blue-800">${path}:</span>
                            <span class="font-medium ${stats.found >= stats.requested ? 'text-green-600' : 'text-orange-600'}">
                                ${stats.found} jobs found (requested: ${stats.requested})
                            </span>
                        </div>
                    `).join('')}
                </div>
                <div class="mt-3 pt-3 border-t border-blue-200">
                    <div class="flex justify-between text-sm font-medium">
                        <span class="text-blue-900">Total Jobs Found:</span>
                        <span class="text-blue-900">${jobResults.total_jobs_found}</span>
                    </div>
                </div>
            </div>
            
            <!-- Jobs by Path -->
            <div class="space-y-6">
                ${Object.entries(jobResults.jobs_by_path).map(([pathTitle, jobs]) => `
                    <div class="border border-gray-200 rounded-lg p-4">
                        <h4 class="font-semibold text-gray-800 mb-3">${pathTitle} (${jobs.length} jobs)</h4>
                        <div class="space-y-3 max-h-96 overflow-y-auto">
                            ${jobs.slice(0, 10).map(job => `
                                <div class="p-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors">
                                    <div class="flex justify-between items-start">
                                        <div class="flex items-start flex-1">
                                            <input type="checkbox" 
                                                class="job-checkbox mt-1 mr-3 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded cursor-pointer"
                                                data-job-id="${job.url}"
                                                data-job-title="${job.title}"
                                                data-job-company="${job.company}"
                                                data-job-description="${job.description}"
                                                data-career-path="${pathTitle}">
                                            <h5 class="font-medium text-gray-900">
                                                <a href="${job.url}" target="_blank" class="hover:text-indigo-600">
                                                    ${job.title}
                                                </a>
                                            </h5>
                                            <p class="text-sm text-gray-600 mt-1">${job.company} • ${job.location}</p>
                                            ${job.salary_range ? `
                                                <p class="text-sm text-green-600 mt-1">
                                                    $${(job.salary_range.min / 1000).toFixed(0)}k - $${(job.salary_range.max / 1000).toFixed(0)}k
                                                </p>
                                            ` : ''}
                                            <p class="text-xs text-gray-500 mt-1">Posted: ${job.posted_date}</p>
                                        </div>
                                        <a href="${job.url}" target="_blank" class="ml-4 text-indigo-600 hover:text-indigo-800">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                            </svg>
                                        </a>
                                    </div>
                                </div>
                            `).join('')}
                            ${jobs.length > 10 ? `
                                <p class="text-sm text-gray-500 text-center mt-2">
                                    Showing 10 of ${jobs.length} jobs
                                </p>
                            ` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <!-- Selection Summary and Action Buttons -->
            <div class="mt-6 space-y-4">
                <!-- Selection Summary -->
                <div id="jobs-selection-summary" class="hidden p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                    <p class="text-sm font-medium text-indigo-800">Selected Jobs: <span id="selected-jobs-count">0</span></p>
                    <div id="selected-jobs-list" class="mt-2 text-sm text-indigo-600 space-y-1"></div>
                </div>
                
                <!-- Action Buttons -->
                <div class="flex gap-4">
                    <button id="backToPathsBtn" class="flex-1 bg-gray-200 text-gray-700 font-semibold py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors">
                        Back to Career Paths
                    </button>
                    <button id="generateResumesBtn" class="flex-1 bg-indigo-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-indigo-700 transition-colors opacity-50 cursor-not-allowed" disabled>
                        Generate Tailored Resumes
                    </button>
                    <button id="exportJobsBtn" class="flex-1 bg-gray-200 text-gray-700 font-semibold py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors">
                        Export Job List
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Replace the current content with job results
    const aiOutput = document.getElementById('ai-output');
    const currentContent = aiOutput.innerHTML;
    aiOutput.setAttribute('data-previous-content', currentContent);
    aiOutput.innerHTML = jobResultsHTML;
    
    // Track selected jobs
    let selectedJobs = new Set();
    
    // Add event listeners for new buttons and checkboxes
    document.getElementById('backToPathsBtn').addEventListener('click', () => {
        // Restore previous content
        aiOutput.innerHTML = aiOutput.getAttribute('data-previous-content');
    });
    
    document.getElementById('exportJobsBtn').addEventListener('click', () => {
        // Export jobs to CSV or JSON
        const dataStr = JSON.stringify(jobResults, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `job-search-results-${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    });

    // Add event listener for job checkboxes
    document.querySelectorAll('.job-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const jobId = checkbox.dataset.jobId;
            const jobTitle = checkbox.dataset.jobTitle;
            const jobCompany = checkbox.dataset.jobCompany;
            const jobDescription = checkbox.dataset.jobDescription;
            const careerPath = checkbox.dataset.careerPath;
            
            if (checkbox.checked) {
                selectedJobs.add({
                    id: jobId,
                    title: jobTitle,
                    company: jobCompany,
                    description: jobDescription,
                    careerPath: careerPath
                });
            } else {
                selectedJobs.delete([...selectedJobs].find(job => job.id === jobId));
            }
            
            // Update selection summary
            const summaryDiv = document.getElementById('jobs-selection-summary');
            const countSpan = document.getElementById('selected-jobs-count');
            const listDiv = document.getElementById('selected-jobs-list');
            const generateBtn = document.getElementById('generateResumesBtn');
            
            if (selectedJobs.size > 0) {
                summaryDiv.classList.remove('hidden');
                countSpan.textContent = selectedJobs.size;
                listDiv.innerHTML = [...selectedJobs].map(job => 
                    `<div class="flex justify-between">
                        <span>${job.title} at ${job.company}</span>
                        <span class="text-indigo-500">${job.careerPath}</span>
                    </div>`
                ).join('');
                generateBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                generateBtn.disabled = false;
            } else {
                summaryDiv.classList.add('hidden');
                generateBtn.classList.add('opacity-50', 'cursor-not-allowed');
                generateBtn.disabled = true;
            }
        });
    });

    // Add event listener for generate resumes button
    document.getElementById('generateResumesBtn').addEventListener('click', () => {
        if (selectedJobs.size > 0) {
            // Show theme selection modal
            showThemeSelectionModal([...selectedJobs]);
        }
    });
}

// Function to show theme selection modal
function showThemeSelectionModal(selectedJobs) {
    // Create modal HTML
    const modalHTML = `
        <div id="theme-selection-modal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <!-- Modal Header -->
                    <div class="flex justify-between items-center pb-4 border-b">
                        <h3 class="text-lg font-semibold text-gray-900">Choose Resume Theme</h3>
                        <button id="close-theme-modal" class="text-gray-400 hover:text-gray-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Selected Jobs Summary -->
                    <div class="mt-4 p-3 bg-gray-50 rounded-lg">
                        <p class="text-sm font-medium text-gray-700">Generating resumes for ${selectedJobs.length} selected job${selectedJobs.length > 1 ? 's' : ''}:</p>
                        <div class="mt-2 space-y-1">
                            ${selectedJobs.map(job => `
                                <div class="text-sm text-gray-600">• ${job.title} at ${job.company}</div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <!-- Theme Selection -->
                    <div class="mt-6">
                        <p class="text-sm font-medium text-gray-700 mb-4">Select a theme for your tailored resumes:</p>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <!-- Flat Theme -->
                            <label class="theme-option cursor-pointer">
                                <input type="radio" name="resume-theme" value="flat" class="sr-only">
                                <div class="border-2 border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition-colors theme-card">
                                    <div class="flex items-center justify-between mb-3">
                                        <h4 class="font-semibold text-gray-900">Flat Theme</h4>
                                        <div class="w-4 h-4 border-2 border-gray-300 rounded-full theme-radio"></div>
                                    </div>
                                    <div class="bg-gray-100 rounded p-3 mb-3">
                                        <div class="space-y-2">
                                            <div class="h-3 bg-gray-300 rounded w-3/4"></div>
                                            <div class="h-2 bg-gray-300 rounded w-1/2"></div>
                                            <div class="h-2 bg-gray-300 rounded w-2/3"></div>
                                        </div>
                                    </div>
                                    <p class="text-xs text-gray-600">Clean, minimal design. Perfect for ATS systems and traditional companies.</p>
                                </div>
                            </label>
                            
                            <!-- Elegant Theme -->
                            <label class="theme-option cursor-pointer">
                                <input type="radio" name="resume-theme" value="elegant" class="sr-only">
                                <div class="border-2 border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition-colors theme-card">
                                    <div class="flex items-center justify-between mb-3">
                                        <h4 class="font-semibold text-gray-900">Elegant Theme</h4>
                                        <div class="w-4 h-4 border-2 border-gray-300 rounded-full theme-radio"></div>
                                    </div>
                                    <div class="bg-gradient-to-r from-gray-100 to-gray-200 rounded p-3 mb-3">
                                        <div class="space-y-2">
                                            <div class="h-3 bg-gray-400 rounded w-3/4"></div>
                                            <div class="h-2 bg-gray-400 rounded w-1/2"></div>
                                            <div class="h-2 bg-gray-400 rounded w-2/3"></div>
                                        </div>
                                    </div>
                                    <p class="text-xs text-gray-600">Professional design with subtle styling. Great for creative and tech roles.</p>
                                </div>
                            </label>
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="mt-6 flex gap-3">
                        <button id="cancel-theme-selection" class="flex-1 bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors">
                            Cancel
                        </button>
                        <button id="generate-with-theme" class="flex-1 bg-indigo-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors opacity-50 cursor-not-allowed" disabled>
                            Generate Resumes
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Add event listeners
    const modal = document.getElementById('theme-selection-modal');
    const closeBtn = document.getElementById('close-theme-modal');
    const cancelBtn = document.getElementById('cancel-theme-selection');
    const generateBtn = document.getElementById('generate-with-theme');
    const themeOptions = document.querySelectorAll('.theme-option');
    
    // Close modal handlers
    const closeModal = () => {
        modal.remove();
    };
    
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    // Click outside to close
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Theme selection handlers
    themeOptions.forEach(option => {
        option.addEventListener('click', () => {
            // Remove previous selections
            themeOptions.forEach(opt => {
                opt.querySelector('.theme-card').classList.remove('border-indigo-500', 'bg-indigo-50');
                opt.querySelector('.theme-radio').classList.remove('border-indigo-500', 'bg-indigo-500');
                opt.querySelector('input').checked = false;
            });
            
            // Select current option
            const card = option.querySelector('.theme-card');
            const radio = option.querySelector('.theme-radio');
            const input = option.querySelector('input');
            
            card.classList.add('border-indigo-500', 'bg-indigo-50');
            radio.classList.add('border-indigo-500', 'bg-indigo-500');
            input.checked = true;
            
            // Enable generate button
            generateBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            generateBtn.disabled = false;
        });
    });
    
    // Generate resumes handler
    generateBtn.addEventListener('click', async () => {
        const selectedTheme = document.querySelector('input[name="resume-theme"]:checked')?.value;
        if (selectedTheme && selectedJobs.length > 0) {
            closeModal();
            await generateTailoredResumes(selectedJobs, selectedTheme);
        }
    });
}

// Function to generate tailored resumes
async function generateTailoredResumes(selectedJobs, theme) {
    // Show loading state
    const generateBtn = document.getElementById('generateResumesBtn');
    const originalText = generateBtn.innerHTML;
    generateBtn.innerHTML = '<span class="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>Generating...';
    generateBtn.disabled = true;
    
    try {
        // Get user data for resume generation
        const userData = {
            linkedin_url: document.getElementById('linkedin_profile').value.trim(),
            personal_story: document.getElementById('personal_story').value.trim(),
            sample_resume: document.getElementById('sample_resume').value.trim()
        };
        
        const results = [];
        
        // Generate resume for each selected job
        for (const job of selectedJobs) {
            try {
                // Call resume generation API (placeholder for now)
                const response = await fetch('http://localhost:8003/api/generate-resume', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        job_description: job.description,
                        job_title: job.title,
                        company: job.company,
                        career_path: job.careerPath,
                        theme: theme,
                        user_data: userData
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    results.push({
                        job: job,
                        success: true,
                        download_url: result.download_url,
                        filename: result.filename
                    });
                } else {
                    throw new Error(`API Error: ${response.status}`);
                }
            } catch (error) {
                console.error(`Error generating resume for ${job.title}:`, error);
                results.push({
                    job: job,
                    success: false,
                    error: error.message
                });
            }
        }
        
        // Show results
        showResumeGenerationResults(results, theme);
        
    } catch (error) {
        console.error('Error in resume generation process:', error);
        showError('Failed to generate resumes. Please try again.');
    } finally {
        // Reset button state
        generateBtn.innerHTML = originalText;
        generateBtn.disabled = false;
    }
}

// Function to show resume generation results
function showResumeGenerationResults(results, theme) {
    const successCount = results.filter(r => r.success).length;
    const failCount = results.length - successCount;
    
    const resultsHTML = `
        <div id="resume-results-modal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <!-- Modal Header -->
                    <div class="flex justify-between items-center pb-4 border-b">
                        <h3 class="text-lg font-semibold text-gray-900">Resume Generation Results</h3>
                        <button id="close-results-modal" class="text-gray-400 hover:text-gray-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Summary -->
                    <div class="mt-4 p-4 ${successCount > 0 ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'} rounded-lg">
                        <p class="font-medium ${successCount > 0 ? 'text-green-800' : 'text-red-800'}">
                            ${successCount} of ${results.length} resumes generated successfully using ${theme} theme
                        </p>
                        ${failCount > 0 ? `<p class="text-sm text-red-600 mt-1">${failCount} failed to generate</p>` : ''}
                    </div>
                    
                    <!-- Results List -->
                    <div class="mt-4 space-y-3 max-h-96 overflow-y-auto">
                        ${results.map(result => `
                            <div class="flex items-center justify-between p-3 border rounded-lg ${result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}">
                                <div class="flex-1">
                                    <p class="font-medium text-gray-900">${result.job.title}</p>
                                    <p class="text-sm text-gray-600">${result.job.company}</p>
                                    ${result.success ? 
                                        `<p class="text-xs text-green-600 mt-1">Resume generated: ${result.filename}</p>` :
                                        `<p class="text-xs text-red-600 mt-1">Error: ${result.error}</p>`
                                    }
                                </div>
                                ${result.success ? `
                                    <a href="${result.download_url}" download="${result.filename}" 
                                       class="ml-4 bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700 transition-colors">
                                        Download
                                    </a>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="mt-6 flex gap-3">
                        <button id="close-results" class="flex-1 bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors">
                            Close
                        </button>
                        ${successCount > 0 ? `
                            <button id="download-all" class="flex-1 bg-indigo-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors">
                                Download All (${successCount})
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', resultsHTML);
    
    // Add event listeners
    const modal = document.getElementById('resume-results-modal');
    const closeBtn = document.getElementById('close-results-modal');
    const closeResultsBtn = document.getElementById('close-results');
    const downloadAllBtn = document.getElementById('download-all');
    
    // Close modal handlers
    const closeModal = () => {
        modal.remove();
    };
    
    closeBtn.addEventListener('click', closeModal);
    closeResultsBtn.addEventListener('click', closeModal);
    
    // Download all handler
    if (downloadAllBtn) {
        downloadAllBtn.addEventListener('click', () => {
            results.filter(r => r.success).forEach(result => {
                const link = document.createElement('a');
                link.href = result.download_url;
                link.download = result.filename;
                link.click();
            });
        });
    }
    
    // Click outside to close
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
}
