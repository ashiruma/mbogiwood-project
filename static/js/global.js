// account.js
// Handles tab switching and dynamic content visibility for the user account page.

document.addEventListener('DOMContentLoaded', function() {
    const navContainer = document.getElementById('account-nav');
    const contentContainer = document.getElementById('account-content');

    if (!navContainer || !contentContainer) {
        return; // Exit if the main containers aren't on the page
    }

    const navButtons = navContainer.querySelectorAll('button[data-tab]');
    const contentDivs = contentContainer.querySelectorAll('div[data-content]');

    // --- Dynamic Content Simulation ---
    // In a real Django app, you would pass the user's role from the backend,
    // for example, by setting a data attribute on the body tag: <body data-user-role="approved_creator">
    const userRole = document.body.dataset.userRole || 'approved_creator'; // Default for demo

    const viewerDashboard = document.getElementById('viewer-dashboard');
    const pendingDashboard = document.getElementById('creator-pending-dashboard');
    const approvedDashboard = document.getElementById('creator-approved-dashboard');
    const myFilmsTab = navContainer.querySelector('[data-tab="my-films"]');

    // Configure the dashboard based on the user's role
    if (userRole === 'approved_creator') {
        if (viewerDashboard) viewerDashboard.classList.add('hidden');
        if (pendingDashboard) pendingDashboard.classList.add('hidden');
        if (approvedDashboard) approvedDashboard.classList.remove('hidden');
        if (myFilmsTab) myFilmsTab.classList.remove('hidden');
    } else if (userRole === 'pending_creator') {
        if (viewerDashboard) viewerDashboard.classList.add('hidden');
        if (pendingDashboard) pendingDashboard.classList.remove('hidden');
        if (approvedDashboard) approvedDashboard.classList.add('hidden');
        if (myFilmsTab) myFilmsTab.classList.add('hidden');
    } else { // Default to 'viewer'
        if (viewerDashboard) viewerDashboard.classList.remove('hidden');
        if (pendingDashboard) pendingDashboard.classList.add('hidden');
        if (approvedDashboard) approvedDashboard.classList.add('hidden');
        if (myFilmsTab) myFilmsTab.classList.add('hidden');
    }

    // --- Tab Switching Logic ---
    navContainer.addEventListener('click', (event) => {
        const targetButton = event.target.closest('button[data-tab]');
        if (!targetButton) return; // Ignore clicks that aren't on a tab button

        const tabName = targetButton.dataset.tab;

        // Update button active styles
        navButtons.forEach(btn => {
            btn.classList.remove('bg-brand-green', 'text-white');
            btn.classList.add('hover:bg-brand-brown-light');
        });
        targetButton.classList.add('bg-brand-green', 'text-white');
        targetButton.classList.remove('hover:bg-brand-brown-light');

        // Update content visibility
        contentDivs.forEach(div => {
            div.classList.toggle('hidden', div.dataset.content !== tabName);
        });
    });
});

