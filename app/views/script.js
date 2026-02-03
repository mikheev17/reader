
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in (simplified)
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    if (window.location.pathname === '/dashboard.html' && !isLoggedIn) {
        window.location.href = '/login.html';
    }

    // Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Animation observer for features
    const featureObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                featureObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.feature-item').forEach(item => {
        featureObserver.observe(item);
    });
});