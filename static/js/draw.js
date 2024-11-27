document.addEventListener('DOMContentLoaded', function() {
    // Add a state tracker for sort direction
    const sortStates = {};
    
    document.querySelectorAll('th.sortable').forEach(headerCell => {
        const column = headerCell.dataset.sort;
        sortStates[column] = 'desc'; // Initial state: desc -> asc -> desc
        
        headerCell.addEventListener('click', () => {
            const table = document.getElementById('artworkTable');
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            
            // Toggle between asc and desc only
            sortStates[column] = sortStates[column] === 'asc' ? 'desc' : 'asc';
            
            // Update sort indicators
            document.querySelectorAll('th.sortable').forEach(th => {
                th.classList.remove('asc', 'desc');
            });
            headerCell.classList.add(sortStates[column]);
            
            // Sort rows
            rows.sort((a, b) => {
                const aValue = a.querySelector(`.${column}`).textContent;
                const bValue = b.querySelector(`.${column}`).textContent;
                
                if (column === 'art-id' || column === 'ranking') {
                    return sortStates[column] === 'asc' ? 
                        Number(aValue) - Number(bValue) : 
                        Number(bValue) - Number(aValue);
                }
                return sortStates[column] === 'asc' ? 
                    aValue.localeCompare(bValue) : 
                    bValue.localeCompare(aValue);
            });
            
            // Reorder the table
            const tbody = table.querySelector('tbody');
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
        });
    });

    // Add form submission handler
    document.getElementById('markWonForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Prevent double submission
        if (this.dataset.submitting === 'true') return;
        this.dataset.submitting = 'true';
        
        const submitButton = this.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        
        const artId = document.getElementById('artId').value;
        const statusMessage = document.getElementById('statusMessage');
        
        fetch(`/mark_won/${artId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json().then(data => {
            if (!response.ok) {
                throw new Error(data.error || 'Failed to mark artwork');
            }
            return data;
        }))
        .then(data => {
            if (data.success) {
                statusMessage.className = 'alert alert-success mt-2';
                statusMessage.style.transition = 'opacity 0.5s ease';
                statusMessage.style.opacity = '1';
                statusMessage.textContent = 'Artwork marked as won successfully!';
                
                // Fade out status message after 5 seconds
                setTimeout(() => {
                    statusMessage.style.opacity = '0';
                    // Remove the message after fade out
                    setTimeout(() => {
                        statusMessage.textContent = '';
                        statusMessage.className = 'mt-2';  // Remove alert classes
                    }, 500);
                }, 5000);
                
                document.getElementById('artId').value = ''; // Clear input
                
                // Find and remove the row
                const artwork = data.artwork;
                const table = document.getElementById('artworkTable');
                const rows = Array.from(table.querySelectorAll('tbody tr'));
                const row = rows.find(row => 
                    row.querySelector('.art-id').textContent === artwork.art_id.toString()
                );
                
                if (row) {
                    // Find the current highest ranking before removing the row
                    const allRankings = Array.from(table.querySelectorAll('tbody tr .ranking'))
                        .map(cell => parseInt(cell.textContent))
                        .filter(ranking => !isNaN(ranking));
                    const currentHighestRanking = Math.min(...allRankings);
                    
                    // Get the ranking of the removed artwork
                    const removedRanking = parseInt(row.querySelector('.ranking').textContent);
                    
                    // Remove the row
                    row.remove();
                    
                    // After removing the row, fetch and update with new data
                    fetch('/get_next_artworks')
                        .then(response => response.json())
                        .then(data => {
                            console.log('Received data:', data);
                            if (data.success && data.artworks.length > 0) {
                                // Only update the top image if the removed artwork was the highest ranked
                                if (removedRanking === currentHighestRanking) {
                                    const topArtworkContainer = document.querySelector('.col-md-8.mx-auto.text-center');
                                    if (topArtworkContainer) {
                                        // Get the elements we want to update
                                        const rankingTitle = topArtworkContainer.querySelector('h1');
                                        const artworkImage = topArtworkContainer.querySelector('img');
                                        const artworkTitle = topArtworkContainer.querySelector('.card-title');
                                        const artworkArtist = topArtworkContainer.querySelector('.card-text');
                                        
                                        // Fade only the image
                                        artworkImage.style.transition = 'opacity 0.5s ease';
                                        artworkImage.style.opacity = '0';
                                        
                                        setTimeout(() => {
                                            // Update all content
                                            rankingTitle.textContent = `Your #${data.artworks[0].user_ranking} Ranked Artwork`;
                                            artworkImage.src = `/static/images/art/${data.artworks[0].art_id}.jpg`;
                                            artworkImage.alt = data.artworks[0].art_title;
                                            artworkImage.setAttribute('data-bs-target', `#imageModal${data.artworks[0].art_id}`);
                                            artworkTitle.textContent = data.artworks[0].art_title;
                                            artworkArtist.textContent = `By ${data.artworks[0].artist}`;
                                            
                                            // Fade in only the image
                                            requestAnimationFrame(() => {
                                                artworkImage.style.opacity = '1';
                                            });
                                        }, 500);
                                    }
                                    
                                    // Update table rows
                                    const tbody = document.querySelector('#artworkTable tbody');
                                    tbody.innerHTML = '';
                                    data.artworks.forEach(artwork => {
                                        const tr = document.createElement('tr');
                                        tr.innerHTML = `
                                            <td class="art-id">${artwork.art_id}</td>
                                            <td class="title">
                                                <span style="cursor: pointer;" 
                                                      data-bs-toggle="modal" 
                                                      data-bs-target="#imageModal${artwork.art_id}">
                                                    ${artwork.art_title}
                                                </span>
                                            </td>
                                            <td class="artist">${artwork.artist}</td>
                                            <td class="price">${artwork.price.toLocaleString().replace(',', ' ')} kr</td>
                                            <td class="ranking">${artwork.user_ranking > 0 ? artwork.user_ranking : '-'}</td>
                                        `;
                                        tbody.appendChild(tr);

                                        // Create or update the modal for this artwork
                                        let modal = document.getElementById(`imageModal${artwork.art_id}`);
                                        if (!modal) {
                                            modal = document.createElement('div');
                                            modal.id = `imageModal${artwork.art_id}`;
                                            modal.className = 'modal fade';
                                            modal.setAttribute('tabindex', '-1');
                                            modal.setAttribute('aria-labelledby', `imageModalLabel${artwork.art_id}`);
                                            modal.setAttribute('aria-hidden', 'true');
                                            modal.innerHTML = `
                                                <div class="modal-dialog modal-fullscreen">
                                                    <div class="modal-content bg-dark">
                                                        <div class="modal-body p-0 d-flex align-items-center justify-content-center" 
                                                             style="min-height: 100vh;"
                                                             data-bs-dismiss="modal">
                                                            <div class="position-relative" style="max-height: 95vh; max-width: 95vw;">
                                                                <button type="button" 
                                                                        class="btn-close btn-close-white position-absolute top-0 end-0 m-3" 
                                                                        data-bs-dismiss="modal" 
                                                                        aria-label="Close"
                                                                        style="z-index: 1050;">
                                                                </button>
                                                                <img src="/static/images/art/${artwork.art_id}.jpg"
                                                                     class="img-fluid"
                                                                     style="max-height: 95vh; max-width: 95vw; object-fit: contain;"
                                                                     alt="${artwork.art_title}"
                                                                     onclick="event.stopPropagation();">
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            `;
                                            document.body.appendChild(modal);
                                        }
                                    });
                                }
                            }
                        })
                        .catch(error => console.error('Error:', error));
                }
            }
        })
        .catch(error => {
            statusMessage.className = 'alert alert-danger mt-2';
            statusMessage.style.transition = 'opacity 0.5s ease';
            statusMessage.style.opacity = '1';
            statusMessage.textContent = `Error: ${error.message}`;
            
            // Fade out error message after 5 seconds
            setTimeout(() => {
                statusMessage.style.opacity = '0';
                // Remove the message after fade out
                setTimeout(() => {
                    statusMessage.textContent = '';
                    statusMessage.className = 'mt-2';  // Remove alert classes
                }, 500);
            }, 5000);
            
            document.getElementById('artId').value = ''; // Clear input on error too
        })
        .finally(() => {
            submitButton.disabled = false;
            this.dataset.submitting = 'false';  // Reset submission flag
        });
    });
}); 