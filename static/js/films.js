// static/js/films.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const filmGrid = document.getElementById('film-grid');
    const paginationContainer = document.getElementById('pagination-container');
    const genreFilter = document.getElementById('genre-filter');
    const sortFilter = document.getElementById('sort-filter');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // The base API endpoint we are calling
    const API_BASE_URL = '/api/v1/videos/';

    /**
     * Fetches film data from a given API URL and updates the page.
     * @param {string} url - The full API URL to fetch from (including any query parameters).
     */
    const fetchFilms = async (url) => {
        // Ensure all required DOM elements are present before proceeding.
        if (!filmGrid || !paginationContainer || !loadingIndicator) {
            console.error("Critical page elements are missing. Cannot fetch films.");
            return;
        }

        loadingIndicator.classList.remove('hidden');
        filmGrid.innerHTML = ''; // Clear the grid to show the loading state

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            
            renderFilms(data.results);
            renderPagination(data);

        } catch (error) {
            filmGrid.innerHTML = `<p class="col-span-full text-center text-red-400">Failed to load films. Please try refreshing the page.</p>`;
            console.error("Error fetching films:", error);
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    };

    /**
     * Renders an array of film objects into the film grid.
     * @param {Array} films - The array of film data from the API.
     */
    const renderFilms = (films) => {
        if (films.length === 0) {
            filmGrid.innerHTML = `<p class="col-span-full text-center text-gray-400">No films found matching your criteria.</p>`;
            return;
        }

        const filmCardsHTML = films.map(film => {
            const posterUrl = film.file_url || 'https://placehold.co/400x600/1a1a1a/cccccc?text=No+Poster';
            const filmTitle = film.title || 'Untitled Film';
            return `
                <a href="/film-detail.html?id=${film.id}" class="group cursor-pointer">
                    <div class="aspect-[2/3] rounded-md overflow-hidden shadow-2xl transform group-hover:-translate-y-2 transition-transform duration-300 border-2 border-transparent group-hover:border-brand-green">
                        <img src="${posterUrl}" alt="Poster for ${filmTitle}" class="w-full h-full object-cover">
                    </div>
                    <h3 class="mt-2 font-bold text-white truncate">${filmTitle}</h3>
                </a>
            `;
        }).join('');

        filmGrid.innerHTML = filmCardsHTML;
    };

    /**
     * Renders pagination controls based on the API response.
     * @param {object} data - The full paginated response object from the API.
     */
    const renderPagination = (data) => {
        paginationContainer.innerHTML = '';

        let paginationHTML = '';
        
        if (data.previous) {
            paginationHTML += `<button data-url="${data.previous}" class="pagination-btn px-4 py-2 rounded-md hover:bg-brand-brown-light">&laquo; Prev</button>`;
        }

        if (data.next) {
            paginationHTML += `<button data-url="${data.next}" class="pagination-btn px-4 py-2 rounded-md hover:bg-brand-brown-light">Next &raquo;</button>`;
        }
        
        paginationContainer.innerHTML = paginationHTML;
    };
    
    /**
     * Handles changes from filter or sort dropdowns and triggers a new API fetch.
     */
    const handleFilterChange = () => {
        const params = new URLSearchParams();
        
        // Add genre to query if a value is selected
        if (genreFilter && genreFilter.value) {
            params.append('search', genreFilter.value); // Uses DRF SearchFilter
        }
        
        // Add sorting to query if a value is selected
        if (sortFilter && sortFilter.value) {
            params.append('ordering', sortFilter.value);
        }

        const newUrl = `${API_BASE_URL}?${params.toString()}`;
        fetchFilms(newUrl);
    };

    // --- Event Listeners ---
    if (genreFilter) {
        genreFilter.addEventListener('change', handleFilterChange);
    }
    if (sortFilter) {
        sortFilter.addEventListener('change', handleFilterChange);
    }
    
    // Event delegation for pagination buttons
    if (paginationContainer) {
        paginationContainer.addEventListener('click', (e) => {
            if (e.target.matches('.pagination-btn')) {
                const url = e.target.dataset.url;
                if (url) {
                    fetchFilms(url);
                }
            }
        });
    }

    // --- Initial Load ---
    fetchFilms(API_BASE_URL);
});
