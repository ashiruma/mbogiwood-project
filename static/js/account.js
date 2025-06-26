// global.js
// Handles shared interactive elements across the site, like the mobile menu.

document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileNav = document.getElementById('mobile-nav');

    if (mobileMenuButton && mobileNav) {
        mobileMenuButton.addEventListener('click', function() {
            // Toggles the 'hidden' class on the mobile navigation menu
            mobileNav.classList.toggle('hidden');
        });
    }
});

