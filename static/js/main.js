// Main JavaScript file for StyleAI

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Style carousel navigation
    const arrowBtns = document.querySelectorAll('.arrow-btn');
    arrowBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Add carousel functionality here if needed
            console.log('Carousel navigation clicked');
        });
    });
});
