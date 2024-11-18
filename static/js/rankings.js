document.addEventListener('DOMContentLoaded', function() {
    const isMobile = window.matchMedia("(max-width: 768px)").matches;
    const isFirefox = navigator.userAgent.toLowerCase().includes('firefox');
    
    new Sortable(document.getElementById('artworkList'), {
        animation: 150,
        handle: isMobile ? '.drag-handle' : null,
        delayOnTouchOnly: true,
        delay: 150,
        
        // Enhanced scroll settings for Firefox
        autoscroll: true,
        scrollSensitivity: isFirefox ? 150 : 80,  // Increased sensitivity for Firefox
        scrollSpeed: isFirefox ? 50 : 30,         // Increased speed for Firefox
        forceFallback: isFirefox && isMobile,     // Force fallback mode on Firefox mobile
        
        // Reduced touch threshold for better response
        touchStartThreshold: isFirefox ? 3 : 5,
        
        // Visual feedback
        chosenClass: 'sortable-chosen',
        dragClass: 'sortable-drag',
        ghostClass: 'sortable-ghost',
        
        onEnd: function(evt) {
            const items = [...evt.to.children];
            const rankings = items.map((item, index) => ({
                art_id: item.dataset.id,
                rank: index + 1
            }));

            fetch('/update_rankings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ rankings: rankings })
            });

            items.forEach((item, index) => {
                item.querySelector('.rank-number').textContent = index + 1;
            });
        }
    });

    // Add lazy loading for modal images
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('show.bs.modal', function () {
            const img = this.querySelector('.modal-artwork');
            if (img && img.dataset.src) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            }
        });
    });
}); 