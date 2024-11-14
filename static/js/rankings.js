document.addEventListener('DOMContentLoaded', function() {
    const isMobile = window.matchMedia("(max-width: 768px)").matches;
    
    new Sortable(document.getElementById('artworkList'), {
        animation: 150,
        handle: isMobile ? '.drag-handle' : null,
        delayOnTouchOnly: true,
        delay: 150,
        
        // Scroll settings
        autoscroll: true,
        scrollSensitivity: 80,
        scrollSpeed: 30,
        
        // Touch handling
        touchStartThreshold: 5,
        
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
}); 