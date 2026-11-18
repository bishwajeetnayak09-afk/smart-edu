// SmartEdu Client interactivity helpers

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 5 seconds if not closed
    const alerts = document.querySelectorAll('[role="alert"]');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.4s ease';
            setTimeout(() => alert.remove(), 400);
        }, 6000);
    });

    // Close modals on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('[id$="Modal"]').forEach(m => m.classList.add('hidden'));
        }
    });
});
