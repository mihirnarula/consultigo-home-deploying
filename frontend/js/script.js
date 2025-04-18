document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const currentPage = window.location.pathname.split('/').pop();
    
    // Always redirect to home if clicking on the site icon
    const logoElement = document.querySelector('.logo');
    if (logoElement) {
        logoElement.addEventListener('click', () => {
            if (isLoggedIn) {
                window.location.href = 'home.html';
            }
        });
    }
    
    // If not logged in and not on login page, redirect to login
    if (!isLoggedIn && currentPage !== 'index.html' && currentPage !== '') {
        window.location.href = 'index.html';
    }
    
    // If logged in and on login page, redirect to home
    if (isLoggedIn && (currentPage === 'index.html' || currentPage === '')) {
        window.location.href = 'home.html';
    }
    
    // Handle login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // In a real app, you would validate credentials against a server
            // For demo purposes, we'll accept any email/password
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('userEmail', email);
            localStorage.setItem('userName', email.split('@')[0]);
            
            window.location.href = 'home.html';
        });
    }
    
    // Handle logout
    const logoutBtn = document.querySelector('.nav-icons .material-icons:nth-child(3)');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('isLoggedIn');
            window.location.href = 'index.html';
        });
    }
    
    // Handle navigation to profile
    const profileBtn = document.querySelector('.nav-icons .material-icons:nth-child(2)');
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
        
        if (urlParams.has('case')) {
            problemTitle = urlParams.get('case');
            problemType = 'Case Study';
        } else if (urlParams.has('guesstimate')) {
            problemTitle = urlParams.get('guesstimate');
            problemType = 'Guesstimate';
        }
        
        if (problemTitle) {
            // Format the title properly
            problemTitle = problemTitle.split('-').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
            
            document.querySelector('.problem-statement h2').textContent = problemTitle;
            
            // Save the solution text as the user types
            const solutionTextarea = document.querySelector('.solution-textarea');
            if (solutionTextarea) {
                // Load any saved solution
                const savedSolution = localStorage.getItem(`solution-${problemType}-${problemTitle}`);
                if (savedSolution) {
                    solutionTextarea.value = savedSolution;
                }
                
                // Save solution as user types
                solutionTextarea.addEventListener('input', () => {
                    localStorage.setItem(`solution-${problemType}-${problemTitle}`, solutionTextarea.value);
                });
            }
        }
    }
}); 