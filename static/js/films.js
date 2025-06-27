// static/js/films.js

document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = '/api/v1/videos/'; // The endpoint we designed
    const filmGrid = document.getElementById('film-grid');
    const paginationContainer = document.getElementById('pagination-container');
    const genreFilter = document.getElementById('genre-filter');
    const sortFilter = document.getElementById('sort-filter');
    const loadingIndicator = document.getElementById('loading-indicator');

    // --- State Management ---
    let currentPageUrl = API_BASE_URL;

    /**
     * Fetches films from the API and triggers rendering.
     * @param {string} url - The API URL to fetch from.
     */
    const fetchFilms = async (url) => {
        if (!filmGrid || !paginationContainer || !loadingIndicator) {
            console.error("Required elements for films page not found.");
            return;
        }

        loadingIndicator.classList.remove('hidden');
        filmGrid.innerHTML = ''; // Clear existing films

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            renderFilms(data.results);
            renderPagination(data);

        } catch (error) {
            filmGrid.innerHTML = `<p class="text-center text-red-400 col-span-full">Could not load films. Please try again later.</p>`;
            console.error("Failed to fetch films:", error);
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    };

    /**
     * Renders the grid of film posters.
     * @param {Array} films - An array of film objects from the API.
     */
    const renderFilms = (films) => {
        if (films.length === 0) {
            filmGrid.innerHTML = `<p class="text-center text-gray-400 col-span-full">No films found matching your criteria.</p>`;
            return;
        }

        films.forEach(film => {
            // Assumes file_url points to a poster image.
            const posterUrl = film.file_url || 'https://placehold.co/400x600/1a1a1a/cccccc?text=No+Poster';
            
            const filmCard = `
                <a href="/film-detail.html?id=${film.id}" class="group cursor-pointer">
                    <div class="aspect-[2/3] rounded-md overflow-hidden shadow-2xl transform group-hover:-translate-y-2 transition-transform duration-300 border-2 border-transparent group-hover:border-brand-green">
                        <img src="${posterUrl}" alt="Poster for ${film.title}" class="w-full h-full object-cover">
                    </div>
                    <h3 class="mt-2 font-bold text-white truncate">${film.title || 'Untitled Film'}</h3>
                </a>
            `;
            filmGrid.insertAdjacentHTML('beforeend', filmCard);
        });
    };

    /**
     * Renders the pagination controls.
     * @param {object} data - The full paginated response from the API.
     */
    const renderPagination = (data) => {
        paginationContainer.innerHTML = ''; // Clear old pagination

        let paginationHTML = '';
        
        if (data.previous) {
            paginationHTML += `<button data-url="${data.previous}" class="pagination-btn px-4 py-2 rounded-md hover:bg-brand-brown-light">&laquo;</button>`;
        }

        // Note: A more complex implementation could calculate and show page numbers.
        // For simplicity, we just show prev/next.
        const currentPage = new URL(data.next || data.previous || currentPageUrl, window.location.origin).searchParams.get('page') || 1;
        paginationHTML += `<span class="px-4 py-2 rounded-md bg-brand-green text-white">${currentPage}</span>`;

        if (data.next) {
            paginationHTML += `<button data-url="${data.next}" class="pagination-btn px-4 py-2 rounded-md hover:bg-brand-brown-light">&raquo;</button>`;
        }
        
        paginationContainer.innerHTML = paginationHTML;
    };
    
    /**
     * Handles filter changes and constructs the new API URL.
     */
    const handleFilterChange = () => {
        const params = new URLSearchParams();
        
        if (genreFilter && genreFilter.value) {
            params.append('genre', genreFilter.value);
        }
        if (sortFilter && sortFilter.value) {
            params.append('ordering', sortFilter.value);
        }

        currentPageUrl = `${API_BASE_URL}?${params.toString()}`;
        fetchFilms(currentPageUrl);
    };

    // --- Event Listeners ---
    if (genreFilter) {
        genreFilter.addEventListener('change', handleFilterChange);
    }
    if (sortFilter) {
        sortFilter.addEventListener('change', handleFilterChange);
    }
    
    paginationContainer.addEventListener('click', (e) => {
        if (e.target.matches('.pagination-btn')) {
            const url = e.target.dataset.url;
            if (url) {
                fetchFilms(url);
            }
        }
    });

    // --- Initial Load ---
    fetchFilms(currentPageUrl);
});
