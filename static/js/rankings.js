document.addEventListener('DOMContentLoaded', function() {
    // Clear any cached form data
    document.querySelectorAll('form').forEach(form => form.reset());
    document.querySelectorAll('.rank-input').forEach(input => {
        const initialValue = input.getAttribute('value');
        input.value = initialValue;
    });
    
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

    // View switching
    const viewButtons = document.querySelectorAll('[data-view]');
    const listView = document.getElementById('listView');
    const galleryView = document.getElementById('galleryView');

    // Function to sync rankings between views
    function syncRankings(sourceView, targetView) {
        // Get current rankings from source view
        const currentRankings = sourceView === 'gallery' 
            ? Array.from(document.querySelectorAll('.rank-input'))
                .map(input => ({
                    art_id: input.dataset.artId,
                    rank: parseInt(input.value) || Infinity
                }))
            : Array.from(document.querySelectorAll('#artworkList .rank-number'))
                .map(span => ({
                    art_id: span.closest('[data-id]').dataset.id,
                    rank: parseInt(span.textContent) || Infinity
                }));

        // Filter and sort rankings
        const sortedRankings = currentRankings
            .filter(item => item.rank !== Infinity)
            .sort((a, b) => a.rank - b.rank);

        if (targetView === 'list') {
            // Update list view
            const artworkList = document.getElementById('artworkList');
            const items = Array.from(artworkList.children);
            
            // Clear the list
            while (artworkList.firstChild) {
                artworkList.removeChild(artworkList.firstChild);
            }
            
            // Sort items based on rankings
            const sortedItems = items.sort((a, b) => {
                const rankA = sortedRankings.find(r => r.art_id === a.dataset.id)?.rank || Infinity;
                const rankB = sortedRankings.find(r => r.art_id === b.dataset.id)?.rank || Infinity;
                return rankA - rankB;
            });
            
            // Update rank numbers and reinsert items
            sortedItems.forEach((item, index) => {
                const rankNumber = item.querySelector('.rank-number');
                if (rankNumber) {
                    rankNumber.textContent = sortedRankings.find(r => r.art_id === item.dataset.id)?.rank || '';
                }
                artworkList.appendChild(item);
            });
        } else {
            // Update gallery view
            const rankInputs = document.querySelectorAll('.rank-input');
            rankInputs.forEach(input => {
                const ranking = sortedRankings.find(r => r.art_id === input.dataset.artId);
                input.value = ranking ? ranking.rank : '';
            });

            // Reorder gallery items
            const artworkGrid = document.getElementById('artworkGrid');
            const items = Array.from(artworkGrid.children);
            
            // Clear the grid
            while (artworkGrid.firstChild) {
                artworkGrid.removeChild(artworkGrid.firstChild);
            }
            
            // Sort and reinsert items
            const sortedItems = items.sort((a, b) => {
                const rankA = sortedRankings.find(r => r.art_id === a.querySelector('.rank-input').dataset.artId)?.rank || Infinity;
                const rankB = sortedRankings.find(r => r.art_id === b.querySelector('.rank-input').dataset.artId)?.rank || Infinity;
                return rankA - rankB;
            });
            
            sortedItems.forEach(item => {
                artworkGrid.appendChild(item);
            });
        }
    }

    viewButtons.forEach(button => {
        button.addEventListener('click', () => {
            viewButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            if (button.dataset.view === 'list') {
                listView.classList.remove('d-none');
                galleryView.classList.add('d-none');
                syncRankings('gallery', 'list');
            } else {
                listView.classList.add('d-none');
                galleryView.classList.remove('d-none');
                syncRankings('list', 'gallery');
            }
        });
    });

    // Gallery view ranking functionality
    let rankTimeout;
    const rankInputs = document.querySelectorAll('.rank-input');
    
    rankInputs.forEach(input => {
        input.addEventListener('change', function() {
            clearTimeout(rankTimeout);
            
            const newRank = parseInt(this.value);
            const artId = this.dataset.artId;
            
            // Clear invalid input
            if (isNaN(newRank) || newRank < 1 || newRank > rankInputs.length) {
                this.value = '';
                return;
            }
            
            // Get all current rankings and sort them by rank
            let rankingsArray = Array.from(rankInputs)
                .map(inp => ({
                    art_id: inp.dataset.artId,
                    rank: parseInt(inp.value)
                }))
                .sort((a, b) => a.rank - b.rank);
            
            // Find the item we're moving
            const itemToMove = rankingsArray.find(item => item.art_id === artId);
            const oldRank = itemToMove.rank;
            
            // Remove the item from its current position
            rankingsArray = rankingsArray.filter(item => item.art_id !== artId);
            
            // Insert the item at its new position
            rankingsArray.splice(newRank - 1, 0, { art_id: artId, rank: newRank });
            
            // Reassign ranks based on array position
            const newRankings = rankingsArray.map((item, index) => ({
                art_id: item.art_id,
                rank: index + 1
            }));
            
            // Update UI with the new rankings
            rankInputs.forEach(input => {
                const ranking = newRankings.find(r => r.art_id === input.dataset.artId);
                input.disabled = true;
                input.value = ranking.rank;
                input.disabled = false;
            });

            // Reorder gallery items
            const artworkGrid = document.getElementById('artworkGrid');
            const items = Array.from(artworkGrid.children);
            
            // Clear the grid
            while (artworkGrid.firstChild) {
                artworkGrid.removeChild(artworkGrid.firstChild);
            }
            
            // Sort items based on new rankings and reinsert
            const sortedItems = items.sort((a, b) => {
                const rankA = parseInt(a.querySelector('.rank-input').value);
                const rankB = parseInt(b.querySelector('.rank-input').value);
                return rankA - rankB;
            });
            
            // Reinsert items in new order
            sortedItems.forEach(item => {
                artworkGrid.appendChild(item);
            });
            
            // Update database
            rankTimeout = setTimeout(() => {
                fetch('/update_rankings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ rankings: newRankings })
                });
            }, 500);
        });

        // Add input validation
        input.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (value > rankInputs.length) {
                this.value = rankInputs.length;
            }
        });
    });
}); 