// Handle solution submission
async function submitSolution(problemId, solution) {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('You must be logged in to submit a solution.');
        window.location.href = 'index.html';
        return;
    }

    console.log(`Submitting solution for problem ID: ${problemId}`);
    try {
        const response = await fetch(`http://localhost:8000/submissions/${problemId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                answer_text: solution
            })
        });

        console.log(`Response status: ${response.status}`);
        const responseData = await response.json();
        console.log('Response data:', responseData);

        if (!response.ok) {
            throw new Error(responseData.detail || 'Error submitting solution');
        }

        return responseData;
    } catch (error) {
        console.error('Error submitting solution:', error);
        if (error.message) {
            console.error('Error message:', error.message);
        }
        throw error;
    }
}

// Function to extract problem ID from URL parameters
function getProblemIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    let problemId = null;
    
    if (urlParams.has('case')) {
        const caseTitle = urlParams.get('case');
        problemId = getCaseIdFromTitle(caseTitle);
    } else if (urlParams.has('guesstimate')) {
        const guessTitle = urlParams.get('guesstimate');
        problemId = getGuessIdFromTitle(guessTitle);
    } else if (urlParams.has('example')) {
        const exampleTitle = urlParams.get('example');
        problemId = getExampleIdFromTitle(exampleTitle);
    } else if (urlParams.has('framework')) {
        const frameworkTitle = urlParams.get('framework');
        problemId = getFrameworkIdFromTitle(frameworkTitle);
    }
    
    return problemId || 1; // Fallback to ID 1 if no ID found
}

// Mock functions to map titles to IDs (in a real app, you'd fetch these from the backend)
function getCaseIdFromTitle(title) {
    const caseMappings = {
        'market-entry-strategy': 1,
        'cost-reduction-analysis': 2
        // Add more mappings as needed
    };
    return caseMappings[title] || 1;
}

function getGuessIdFromTitle(title) {
    const guessMappings = {
        'market-size-estimation': 3,
        'revenue-estimation': 4,
        'cost-structure-analysis': 5
        // Add more mappings as needed
    };
    return guessMappings[title] || 3;
}

function getExampleIdFromTitle(title) {
    // This will be updated dynamically based on the available examples
    return 1;
}

function getFrameworkIdFromTitle(title) {
    // This will be updated dynamically based on the available frameworks
    return 1;
}

// Function to fetch and display examples
async function loadExamples() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('No token found, redirecting to login');
        window.location.href = 'auth.html';
        return;
    }

    try {
        // Fetch examples for all problem categories
        const response = await fetch('http://localhost:8000/problems/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch problems');
        }

        const problems = await response.json();
        const container = document.querySelector('main');
        
        // Clear existing content except title
        const pageTitle = container.querySelector('.page-title');
        container.innerHTML = '';
        container.appendChild(pageTitle);
        
        // Add examples for each problem
        for (const problem of problems) {
            try {
                const examplesResponse = await fetch(`http://localhost:8000/problems/${problem.problem_id}/examples`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (!examplesResponse.ok) {
                    console.error(`Failed to fetch examples for problem ${problem.problem_id}`);
                    continue;
                }
                
                const examples = await examplesResponse.json();
                
                // Display examples if any exist
                if (examples && examples.length > 0) {
                    // Add problem title as a section header
                    const problemHeader = document.createElement('h2');
                    problemHeader.textContent = problem.title;
                    problemHeader.className = 'problem-category';
                    container.appendChild(problemHeader);
                    
                    // Display each example
                    for (const example of examples) {
                        const card = document.createElement('div');
                        card.className = 'case-card';
                        card.dataset.exampleId = example.example_id;
                        card.dataset.problemId = problem.problem_id;
                        
                        // Create title element
                        const title = document.createElement('h3');
                        // Show full example text
                        title.textContent = example.example_text;
                        
                        // Create difficulty badge
                        const badge = document.createElement('span');
                        badge.className = `difficulty ${problem.difficulty.toLowerCase()}`;
                        badge.textContent = problem.difficulty;
                        
                        // Add elements to card
                        card.appendChild(title);
                        card.appendChild(badge);
                        
                        // Add click event
                        card.addEventListener('click', () => {
                            // Store the example data in localStorage for the detail page
                            localStorage.setItem('currentExample', JSON.stringify(example));
                            window.location.href = `example-detail.html?example=${encodeURIComponent(title.textContent.toLowerCase().replace(/\s+/g, '-'))}&id=${example.example_id}`;
                        });
                        
                        container.appendChild(card);
                    }
                }
            } catch (error) {
                console.error(`Error fetching examples for problem ${problem.problem_id}:`, error);
            }
        }
        
        if (container.querySelectorAll('.case-card').length === 0) {
            const noExamples = document.createElement('p');
            noExamples.className = 'case-instructions';
            noExamples.textContent = 'No examples available yet.';
            container.appendChild(noExamples);
        } else {
            const instructions = document.createElement('p');
            instructions.className = 'case-instructions';
            instructions.textContent = 'Select an example to explore';
            container.appendChild(instructions);
        }
    } catch (error) {
        console.error('Error loading examples:', error);
        const container = document.querySelector('main');
        const errorMsg = document.createElement('p');
        errorMsg.className = 'error-message';
        errorMsg.textContent = 'Failed to load examples. Please try again later.';
        container.appendChild(errorMsg);
    }
}

// Function to fetch and display frameworks
async function loadFrameworks() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('No token found, redirecting to login');
        window.location.href = 'auth.html';
        return;
    }

    try {
        // Fetch problems to get their categories
        const response = await fetch('http://localhost:8000/problems/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch problems');
        }

        const problems = await response.json();
        const container = document.querySelector('main');
        
        // Clear existing content except title
        const pageTitle = container.querySelector('.page-title');
        container.innerHTML = '';
        container.appendChild(pageTitle);
        
        // Add frameworks for each problem
        for (const problem of problems) {
            try {
                const frameworksResponse = await fetch(`http://localhost:8000/problems/${problem.problem_id}/frameworks`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (!frameworksResponse.ok) {
                    console.error(`Failed to fetch frameworks for problem ${problem.problem_id}`);
                    continue;
                }
                
                const frameworks = await frameworksResponse.json();
                
                // Display frameworks if any exist
                if (frameworks && frameworks.length > 0) {
                    // Add problem title as a section header
                    const problemHeader = document.createElement('h2');
                    problemHeader.textContent = problem.title;
                    problemHeader.className = 'problem-category';
                    container.appendChild(problemHeader);
                    
                    // Display each framework
                    for (const framework of frameworks) {
                        const card = document.createElement('div');
                        card.className = 'case-card';
                        card.dataset.frameworkId = framework.framework_id;
                        card.dataset.problemId = problem.problem_id;
                        
                        // Create title element
                        const title = document.createElement('h3');
                        title.textContent = framework.title;
                        
                        // Create difficulty badge
                        const badge = document.createElement('span');
                        badge.className = `difficulty ${problem.difficulty.toLowerCase()}`;
                        badge.textContent = problem.difficulty;
                        
                        // Add elements to card
                        card.appendChild(title);
                        card.appendChild(badge);
                        
                        // Add click event
                        card.addEventListener('click', () => {
                            // Store the framework data in localStorage for the detail page
                            localStorage.setItem('currentFramework', JSON.stringify(framework));
                            window.location.href = `framework-detail.html?framework=${encodeURIComponent(framework.title.toLowerCase().replace(/\s+/g, '-'))}&id=${framework.framework_id}`;
                        });
                        
                        container.appendChild(card);
                    }
                }
            } catch (error) {
                console.error(`Error fetching frameworks for problem ${problem.problem_id}:`, error);
            }
        }
        
        if (container.querySelectorAll('.case-card').length === 0) {
            const noFrameworks = document.createElement('p');
            noFrameworks.className = 'case-instructions';
            noFrameworks.textContent = 'No frameworks available yet.';
            container.appendChild(noFrameworks);
        } else {
            const instructions = document.createElement('p');
            instructions.className = 'case-instructions';
            instructions.textContent = 'Select a framework to learn';
            container.appendChild(instructions);
        }
    } catch (error) {
        console.error('Error loading frameworks:', error);
        const container = document.querySelector('main');
        const errorMsg = document.createElement('p');
        errorMsg.className = 'error-message';
        errorMsg.textContent = 'Failed to load frameworks. Please try again later.';
        container.appendChild(errorMsg);
    }
}

// Function to fetch problem details from API and update the page
async function loadProblemDetails(problemId) {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('You must be logged in to view this problem.');
        window.location.href = 'index.html';
        return;
    }

    try {
        console.log(`Fetching problem details for ID: ${problemId}`);
        const response = await fetch(`http://localhost:8000/problems/${problemId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch problem details');
        }

        const problemData = await response.json();
        console.log('Problem data:', problemData);
        
        // Update page with problem details
        const problemStatement = document.querySelector('.problem-statement');
        if (problemStatement) {
            // Format the description based on problem type
            let formattedDescription = '';
            
            if (problemData.category === 'Case Study') {
                // For case studies, format with background, situation, question, considerations
                formattedDescription = formatCaseStudyDescription(problemData.description);
            } else if (problemData.category === 'Guesstimate') {
                // For guesstimates, format with question, approach, expected output
                formattedDescription = formatGuessDescription(problemData.description);
            } else {
                // Default formatting
                formattedDescription = `<p>${problemData.description}</p>`;
            }
            
            // Update the title
            const titleElement = problemStatement.querySelector('h2');
            if (titleElement) {
                titleElement.textContent = problemData.title;
            }
            
            // Clear existing content except the title
            const title = problemStatement.querySelector('h2').outerHTML;
            problemStatement.innerHTML = title + formattedDescription;
        }
        
        return problemData;
    } catch (error) {
        console.error('Error fetching problem details:', error);
        const problemStatement = document.querySelector('.problem-statement');
        if (problemStatement) {
            problemStatement.innerHTML += `<p class="error">Error loading problem details: ${error.message}</p>`;
        }
    }
}

// Helper function to format case study descriptions with rich HTML
function formatCaseStudyDescription(description) {
    // If description already contains HTML, return it as is
    if (description.includes('<p>') || description.includes('<ul>')) {
        return description;
    }
    
    // Default rich formatting for case studies
    return `
        <p><strong>Background:</strong> A leading athletic footwear company is considering entering the premium athletic apparel market. They currently have a small presence in basic athletic wear but want to expand into high-performance athletic clothing to compete with established brands.</p>
        
        <p><strong>Current Situation:</strong> The company has strong brand recognition in footwear with $2 billion in annual revenue. Their current athletic apparel line generates only $150 million in revenue (7.5% of total). The premium athletic apparel market is growing at 8% annually and is valued at $45 billion globally.</p>
        
        <p><strong>The Question:</strong> ${description}</p>
        
        <p><strong>Considerations:</strong></p>
        <ul>
            <li>Market dynamics and competitive landscape</li>
            <li>Company's strengths and potential competitive advantages</li>
            <li>Potential go-to-market strategies</li>
            <li>Financial implications and expected ROI</li>
            <li>Potential risks and how to mitigate them</li>
        </ul>
    `;
}

// Helper function to format guesstimate descriptions with rich HTML
function formatGuessDescription(description) {
    // If description already contains HTML, return it as is
    if (description.includes('<p>') || description.includes('<ul>')) {
        return description;
    }
    
    // Default rich formatting for guesstimates
    return `
        <p><strong>The Question:</strong> ${description}</p>
        
        <p><strong>Approach Guidelines:</strong></p>
        <ul>
            <li>Consider the relevant population and demographic segments</li>
            <li>Think about frequency of use or consumption patterns</li>
            <li>Consider different channels and distribution methods</li>
            <li>Make reasonable assumptions and state them clearly</li>
            <li>Structure your calculation in a logical way</li>
        </ul>
        
        <p><strong>Expected Output:</strong> A clear, structured estimation with assumptions, calculations, and a final answer.</p>
    `;
}

// Function to format feedback with scores based on problem type
function formatFeedback(feedback, problemType) {
    // Extract feedback content sections from text
    const feedbackContent = extractFeedbackSections(feedback.feedback_text);
    
    // Set scores based on relevance
    let scores;
    if (feedbackContent.is_relevant === false) {
        // If solution is not relevant, set all scores to 0
        scores = {
            overall_score: 0,
            structure_score: 0,
            quantitative_score: 0,
            creativity_score: 0,
            communication_score: 0
        };
    } else {
        // Use regular fields since raw_json is not available
        scores = {
            overall_score: feedback.overall_score,
            structure_score: feedback.structure_score,
            quantitative_score: feedback.clarity_score,
            creativity_score: feedback.creativity_score,
            communication_score: feedback.confidence_score
        };
    }
    
    // Generate score HTML using definite scores (no fallbacks needed)
    const scoreHtml = generateScoreHtml(scores, problemType);
    
    // Generate feedback sections HTML, passing the overall score
    const feedbackHtml = generateFeedbackHtml(feedbackContent, scores.overall_score);
    
    return scoreHtml + feedbackHtml;
}

// Helper function to extract sections from feedback text
function extractFeedbackSections(feedbackText) {
    const result = {
        relevance: '',
        strengths: [],
        areas_for_improvement: [],
        final_assessment: '',
        is_relevant: true // Default to relevant
    };
    
    // Extract relevance
    const relevanceMatch = feedbackText.match(/Relevance[:\s-]*([^]*?)(?=\n\n|\nStrengths|\nAreas for|$)/i);
    if (relevanceMatch && relevanceMatch[1]) {
        const relevanceText = relevanceMatch[1].trim();
        result.relevance = relevanceText;
        
        // Check if the answer is not relevant
        const notRelevantPattern = /\b(no|not relevant|irrelevant|doesn't address|does not address|off-topic|misses the point|misunderstands|fails to address|unrelated|not applicable|incorrect|completely off|missing the mark|wrong approach|not answering)\b/i;
        if (notRelevantPattern.test(relevanceText)) {
            result.is_relevant = false;
        }
    }
    
    // Extract strengths
    const strengthsMatch = feedbackText.match(/Strengths[:\s-]*([^]*?)(?=\n\n|\nAreas for|Final Assessment|$)/i);
    if (strengthsMatch && strengthsMatch[1]) {
        const strengthsText = strengthsMatch[1].trim();
        
        // Handle bullet points (asterisks or dashes)
        if (strengthsText.includes('* ') || strengthsText.includes('- ')) {
            const bulletPoints = strengthsText.split(/\n[*\-]\s+/).filter(item => item.trim());
            result.strengths = bulletPoints;
        } else {
            result.strengths = [strengthsText];
        }
    }
    
    // Extract areas for improvement
    const improvementMatch = feedbackText.match(/Areas for [iI]mprovement[:\s-]*([^]*?)(?=\n\n|\nFinal Assessment|$)/i);
    if (improvementMatch && improvementMatch[1]) {
        const improvementText = improvementMatch[1].trim();
        
        // Handle bullet points (asterisks or dashes)
        if (improvementText.includes('* ') || improvementText.includes('- ')) {
            const bulletPoints = improvementText.split(/\n[*\-]\s+/).filter(item => item.trim());
            result.areas_for_improvement = bulletPoints;
        } else {
            result.areas_for_improvement = [improvementText];
        }
    }
    
    // Extract final assessment
    const assessmentMatch = feedbackText.match(/Final Assessment[:\s-]*([^]*?)(?=\n\n|$)/i);
    if (assessmentMatch && assessmentMatch[1]) {
        result.final_assessment = assessmentMatch[1].trim();
    }
    
    return result;
}

// Helper function to generate score HTML
function generateScoreHtml(scores, problemType) {
    const overallScore = parseFloat(scores.overall_score) || 0;
    const structureScore = parseFloat(scores.structure_score) || 0;
    const quantitativeScore = parseFloat(scores.quantitative_score) || 0;
    const creativityScore = parseFloat(scores.creativity_score) || 0;
    const communicationScore = parseFloat(scores.communication_score) || 0;
    
    // Check if solution is not relevant (all scores are 0)
    const isNotRelevant = overallScore === 0 && structureScore === 0 && 
                         quantitativeScore === 0 && creativityScore === 0 && 
                         communicationScore === 0;
    
    // Set labels based on problem type
    let structureLabel, quantitativeLabel, creativityLabel, communicationLabel;
    
    if (problemType === 'Case Study') {
        structureLabel = "Structure & Framework";
        quantitativeLabel = "Quantitative Analysis";
        creativityLabel = "Creativity & Insight";
        communicationLabel = "Communication Clarity";
    } else { // Guesstimate
        structureLabel = "Structure & Framework";
        quantitativeLabel = "Quantitative Analysis";
        creativityLabel = "Creativity & Insight";
        communicationLabel = "Communication Clarity"; 
    }
    
    // Create not relevant warning message if needed
    const notRelevantWarning = isNotRelevant ? 
        `<div class="relevance-warning">
            <i class="material-icons">warning</i>
            <p>Solution not relevant to the problem. Please review the problem statement and try again.</p>
        </div>` : '';
    
    return `
    <div class="feedback-scores${isNotRelevant ? ' not-relevant' : ''}">
        ${notRelevantWarning}
        <div class="overall-score">
            <h4>Overall Score</h4>
            <div class="score-value">${overallScore.toFixed(1)}/10</div>
        </div>
        <div class="score-categories">
            <div class="score-item">
                <div class="score-label">${structureLabel}</div>
                <div class="score-number">${structureScore.toFixed(1)}/10</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${(structureScore/10)*100}%"></div>
                </div>
            </div>
            <div class="score-item">
                <div class="score-label">${quantitativeLabel}</div>
                <div class="score-number">${quantitativeScore.toFixed(1)}/10</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${(quantitativeScore/10)*100}%"></div>
                </div>
            </div>
            <div class="score-item">
                <div class="score-label">${creativityLabel}</div>
                <div class="score-number">${creativityScore.toFixed(1)}/10</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${(creativityScore/10)*100}%"></div>
                </div>
            </div>
            <div class="score-item">
                <div class="score-label">${communicationLabel}</div>
                <div class="score-number">${communicationScore.toFixed(1)}/10</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${(communicationScore/10)*100}%"></div>
                </div>
            </div>
        </div>
    </div>`;
}

// Helper function to generate feedback HTML
function generateFeedbackHtml(feedbackContent, overallScore) {
    let relevanceSection = '';
    let strengthsSection = '';
    let improvementSection = '';
    let assessmentSection = '';
    
    // Create relevance section
    if (feedbackContent.relevance) {
        relevanceSection = `<div class="feedback-section">
            <h5>Relevance</h5>
            <p>${feedbackContent.relevance}</p>
        </div>`;
    }
    
    // Create strengths section
    if (feedbackContent.strengths && feedbackContent.strengths.length > 0) {
        const strengthsList = feedbackContent.strengths.length > 1 
            ? '<ul>' + feedbackContent.strengths.map(item => `<li>${item.trim()}</li>`).join('') + '</ul>'
            : `<p>${feedbackContent.strengths[0]}</p>`;
            
        strengthsSection = `<div class="feedback-section">
            <h5>Strengths</h5>
            ${strengthsList}
        </div>`;
    }
    
    // Create areas for improvement section
    if (feedbackContent.areas_for_improvement && feedbackContent.areas_for_improvement.length > 0) {
        const improvementList = feedbackContent.areas_for_improvement.length > 1
            ? '<ul>' + feedbackContent.areas_for_improvement.map(item => `<li>${item.trim()}</li>`).join('') + '</ul>'
            : `<p>${feedbackContent.areas_for_improvement[0]}</p>`;
            
        improvementSection = `<div class="feedback-section">
            <h5>Areas for Improvement</h5>
            ${improvementList}
        </div>`;
    }
    
    // Create final assessment section with overall score
    if (feedbackContent.final_assessment) {
        const scoreDisplay = typeof overallScore !== 'undefined' ? 
            `<p class="final-score">Overall Score: <strong>${parseFloat(overallScore).toFixed(1)}/10</strong></p>` : '';
            
        assessmentSection = `<div class="feedback-section">
            <h5>Final Assessment</h5>
            <p>${feedbackContent.final_assessment}</p>
            ${scoreDisplay}
        </div>`;
    }
    
    // Handle case where no sections were successfully extracted
    if (!relevanceSection && !strengthsSection && !improvementSection && !assessmentSection) {
        // Format as raw text if no structured content
        if (typeof feedbackContent === 'string') {
            return '<div class="feedback-text">' + feedbackContent.replace(/\n/g, '<br>') + '</div>';
        }
        return '<div class="feedback-text"><p>No feedback available.</p></div>';
    }
    
    // Return the combined HTML with properly formatted sections
    return `<div class="feedback-text">
        ${relevanceSection}
        ${strengthsSection}
        ${improvementSection}
        ${assessmentSection}
    </div>`;
}

document.addEventListener('DOMContentLoaded', () => {
    // API base URL
    const API_URL = 'http://localhost:8000';

    // Check if user is logged in
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const token = localStorage.getItem('token');
    const currentPage = window.location.pathname.split('/').pop();
    
    // Always redirect to home if clicking on the site icon
    const logoElement = document.querySelector('.logo');
    if (logoElement) {
        logoElement.addEventListener('click', () => {
            if (isLoggedIn) {
                window.location.href = 'home.html';
            } else {
                window.location.href = 'index.html';
            }
        });
    }
    
    // If not logged in and trying to access a protected page, redirect to login
    if (!isLoggedIn && !['index.html', 'auth.html', ''].includes(currentPage)) {
        window.location.href = 'auth.html';
    }
    
    // If logged in and on login page, redirect to home
    if (isLoggedIn && currentPage === 'auth.html') {
        window.location.href = 'home.html';
    }
    
    // Load examples and frameworks on their respective pages
    if (currentPage === 'examples.html') {
        loadExamples();
    } else if (currentPage === 'frameworks.html') {
        loadFrameworks();
    }
    
    // Handle landing page buttons
    const startPracticingBtns = document.querySelectorAll('.btn-primary[href="auth.html"]');
    if (startPracticingBtns.length) {
        startPracticingBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (isLoggedIn) {
                    e.preventDefault();
                    window.location.href = 'home.html';
                }
            });
        });
    }
    
    // Toggle between login and signup forms
    const signupLink = document.getElementById('signup-link');
    const loginLink = document.getElementById('login-link');
    const loginBox = document.getElementById('login-box');
    const signupBox = document.getElementById('signup-box');
    
    if (signupLink) {
        signupLink.addEventListener('click', (e) => {
            e.preventDefault();
            loginBox.style.display = 'none';
            signupBox.style.display = 'block';
        });
    }
    
    if (loginLink) {
        loginLink.addEventListener('click', (e) => {
            e.preventDefault();
            signupBox.style.display = 'none';
            loginBox.style.display = 'block';
        });
    }
    
    // Handle login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            const errorElement = document.getElementById('login-error');
            
            try {
                // Clear previous error
                errorElement.textContent = '';
                console.log(`Attempting login with: ${email}`);
                
                // Format data for the token endpoint (which uses form data)
                const formData = new FormData();
                formData.append('username', email); // API expects 'username' field
                formData.append('password', password);
                
                // Call the token endpoint
                console.log(`Sending request to ${API_URL}/token`);
                const response = await fetch(`${API_URL}/token`, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Login successful. Token received.');
                    
                    // Store token and user info
                    localStorage.setItem('isLoggedIn', 'true');
                    localStorage.setItem('token', data.access_token);
                    localStorage.setItem('userEmail', email);
                    localStorage.setItem('userName', data.username);
                    localStorage.setItem('userId', data.user_id);
                    
                    // Redirect to home page
                    window.location.href = 'home.html';
                } else {
                    const error = await response.json();
                    console.error('Login failed:', error);
                    errorElement.textContent = error.detail || 'Invalid email or password';
                }
            } catch (error) {
                console.error('Login error:', error);
                errorElement.textContent = 'An error occurred during login. Please try again.';
            }
        });
    }
    
    // Handle signup form submission
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('signup-username').value;
            const email = document.getElementById('signup-email').value;
            const firstName = document.getElementById('signup-firstname').value;
            const lastName = document.getElementById('signup-lastname').value;
            const password = document.getElementById('signup-password').value;
            const errorElement = document.getElementById('signup-error');
            
            try {
                // Clear previous error
                errorElement.textContent = '';
                console.log(`Attempting to create user: ${username}, ${email}`);
                
                // Call the users endpoint to create a new user
                const userData = {
                    username: username,
                    email: email,
                    first_name: firstName,
                    last_name: lastName,
                    password: password
                };
                
                console.log('Signup data:', userData);
                console.log(`Sending request to ${API_URL}/users/`);
                
                const response = await fetch(`${API_URL}/users/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Signup successful:', data);
                    
                    // Show login form with success message
                    signupBox.style.display = 'none';
                    loginBox.style.display = 'block';
                    document.getElementById('login-error').textContent = 'Account created! Please log in.';
                    document.getElementById('login-error').style.color = '#4CAF50';
                } else {
                    const error = await response.json();
                    console.error('Signup failed:', error);
                    errorElement.textContent = error.detail || 'Error creating account. Please try again.';
                }
            } catch (error) {
                console.error('Signup error:', error);
                errorElement.textContent = 'An error occurred during signup. Please try again.';
            }
        });
    }
    
    // Handle solution submission
    const submitSolutionBtn = document.getElementById('submit-solution');
    if (submitSolutionBtn) {
        submitSolutionBtn.addEventListener('click', async () => {
            // Get the solution text
            const solutionText = document.querySelector('.solution-textarea').value;
            if (!solutionText.trim()) {
                alert('Please enter your solution before submitting.');
                return;
            }
            
            // Get problem ID from URL
            const problemId = getProblemIdFromUrl();
            if (!problemId) {
                alert('Unable to determine the problem ID. Please try again or contact support.');
                return;
            }
            
            console.log(`Submitting solution for problem ID: ${problemId}`);
            
            // Show loading indicator
            const feedbackContainer = document.querySelector('.feedback-container');
            const loadingIndicator = document.querySelector('.loading-indicator');
            const feedbackContent = document.querySelector('.feedback-content');
            
            feedbackContainer.style.display = 'block';
            loadingIndicator.style.display = 'block';
            feedbackContent.textContent = '';
            
            try {
                // Submit solution and get feedback
                const feedback = await submitSolution(problemId, solutionText);
                
                // Hide loading indicator and show feedback
                loadingIndicator.style.display = 'none';
                
                // Get problem type for correct formatting
                const currentPage = window.location.pathname.split('/').pop();
                const urlParams = new URLSearchParams(window.location.search);
                let problemTitle = '';
                let problemType = '';
                
                if (currentPage.includes('case-detail') && urlParams.has('case')) {
                    problemTitle = urlParams.get('case');
                    problemType = 'Case Study';
                } else if (currentPage.includes('guesstimate-detail') && urlParams.has('guesstimate')) {
                    problemTitle = urlParams.get('guesstimate');
                    problemType = 'Guesstimate';
                }
                
                // Format the title properly for localStorage
                problemTitle = problemTitle.split('-').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                ).join(' ');
                
                // Format and display the feedback
                feedbackContent.innerHTML = formatFeedback(feedback, problemType);
                
                // Save solution and feedback to localStorage
                localStorage.setItem(`solution-${problemType}-${problemTitle}`, solutionText);
                localStorage.setItem(`feedback-${problemType}-${problemTitle}`, feedback.feedback_text);
                localStorage.setItem(`feedback-data-${problemType}-${problemTitle}`, JSON.stringify(feedback));
                
            } catch (error) {
                // Show error message
                console.error('Error in submit handler:', error);
                loadingIndicator.style.display = 'none';
                
                // Create a more user-friendly error message
                let errorMessage = 'Unable to generate feedback.';
                
                if (error && error.message) {
                    errorMessage += ` ${error.message}`;
                } else if (typeof error === 'string') {
                    errorMessage += ` ${error}`;
                } else if (error && typeof error === 'object') {
                    errorMessage += ' Please try again later.';
                    console.error('Detailed error object:', JSON.stringify(error));
                }
                
                feedbackContent.textContent = `Error: ${errorMessage}`;
                feedbackContent.style.color = '#e53e3e';
            }
        });
    }
    
    // Handle logout
    const logoutBtn = document.querySelector('.nav-icons .material-icons:nth-child(2)');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('isLoggedIn');
            localStorage.removeItem('token');
            localStorage.removeItem('userEmail');
            localStorage.removeItem('userName');
            localStorage.removeItem('userId');
            window.location.href = 'index.html';
        });
    }
    
    // Handle navigation to profile
    const profileBtn = document.querySelector('.nav-icons .material-icons:nth-child(1)');
    if (profileBtn) {
        profileBtn.addEventListener('click', () => {
            window.location.href = 'profile.html';
        });
    }
    
    // Load user data in profile page
    const profilePage = document.querySelector('.profile-container');
    if (profilePage) {
        const userName = localStorage.getItem('userName') || 'User';
        const userEmail = localStorage.getItem('userEmail') || 'user@example.com';
        
        document.querySelector('.profile-info h2').textContent = userName;
        document.querySelector('.profile-info p').textContent = userEmail;
    }
    
    // Add click events to cards on homepage
    const cards = document.querySelectorAll('.card');
    if (cards.length) {
        cards.forEach(card => {
            card.addEventListener('click', () => {
                const cardTitle = card.querySelector('h3').textContent.toLowerCase().replace(/\s+/g, '-');
                window.location.href = `${cardTitle}.html`;
            });
        });
    }
    
    // Add click events to case study cards to navigate to detailed problem pages
    const caseCards = document.querySelectorAll('.case-card');
    if (caseCards.length) {
        caseCards.forEach(card => {
            card.addEventListener('click', () => {
                const cardTitle = card.querySelector('h3').textContent.toLowerCase().replace(/\s+/g, '-');
                const currentPage = window.location.pathname.split('/').pop();
                
                if (currentPage.includes('case-studies')) {
                    window.location.href = `case-detail.html?case=${cardTitle}`;
                } else if (currentPage.includes('guesstimates')) {
                    window.location.href = `guesstimate-detail.html?guesstimate=${cardTitle}`;
                } else if (currentPage.includes('frameworks')) {
                    window.location.href = `framework-detail.html?framework=${cardTitle}`;
                } else if (currentPage.includes('examples')) {
                    window.location.href = `example-detail.html?example=${cardTitle}`;
                }
            });
        });
    }
    
    // Handle problem details page
    const problemContainer = document.querySelector('.problem-container');
    if (problemContainer) {
        // Get the case or guesstimate from URL
        const urlParams = new URLSearchParams(window.location.search);
        let problemTitle = '';
        let problemType = '';
        let problemId = null;
        
        if (urlParams.has('case')) {
            problemTitle = urlParams.get('case');
            problemType = 'Case Study';
            problemId = getCaseIdFromTitle(problemTitle);
        } else if (urlParams.has('guesstimate')) {
            problemTitle = urlParams.get('guesstimate');
            problemType = 'Guesstimate';
            problemId = getGuessIdFromTitle(problemTitle);
        }
        
        if (problemId) {
            // Load the problem details from API
            loadProblemDetails(problemId).then(problemData => {
                // Format the title properly for localStorage keys
                const formattedTitle = problemTitle.split('-').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                ).join(' ');
                
                // Save the solution text as the user types
                const solutionTextarea = document.querySelector('.solution-textarea');
                if (solutionTextarea) {
                    // Load any saved solution
                    const savedSolution = localStorage.getItem(`solution-${problemType}-${formattedTitle}`);
                    if (savedSolution) {
                        solutionTextarea.value = savedSolution;
                        
                        // Check if there's also saved feedback to display
                        const savedFeedback = localStorage.getItem(`feedback-${problemType}-${formattedTitle}`);
                        const savedFeedbackData = localStorage.getItem(`feedback-data-${problemType}-${formattedTitle}`);
                        
                        if (savedFeedback) {
                            const feedbackContainer = document.querySelector('.feedback-container');
                            const feedbackContent = document.querySelector('.feedback-content');
                            
                            feedbackContainer.style.display = 'block';
                            
                            // If we have saved feedback data (with scores)
                            if (savedFeedbackData) {
                                try {
                                    const feedbackData = JSON.parse(savedFeedbackData);
                                    feedbackContent.innerHTML = formatFeedback(feedbackData, problemType);
                                } catch (e) {
                                    // Fallback to just text if parsing fails
                                    feedbackContent.textContent = savedFeedback;
                                }
                            } else {
                                // Just use the text
                                feedbackContent.textContent = savedFeedback;
                            }
                        }
                        
                        // Save solution as user types
                        solutionTextarea.addEventListener('input', () => {
                            localStorage.setItem(`solution-${problemType}-${formattedTitle}`, solutionTextarea.value);
                        });
                    }
                }
                
                // Clear solution and feedback when the user leaves the page
                window.addEventListener('beforeunload', () => {
                    console.log('User is leaving the page, clearing solution and feedback');
                    
                    // Clear textarea
                    if (solutionTextarea) {
                        solutionTextarea.value = '';
                    }
                    
                    // Clear feedback display
                    const feedbackContainer = document.querySelector('.feedback-container');
                    const feedbackContent = document.querySelector('.feedback-content');
                    if (feedbackContainer) {
                        feedbackContainer.style.display = 'none';
                    }
                    if (feedbackContent) {
                        feedbackContent.innerHTML = '';
                    }
                    
                    // Remove items from localStorage
                    localStorage.removeItem(`solution-${problemType}-${formattedTitle}`);
                    localStorage.removeItem(`feedback-${problemType}-${formattedTitle}`);
                    localStorage.removeItem(`feedback-data-${problemType}-${formattedTitle}`);
                });
            });
        }
    }
}); 