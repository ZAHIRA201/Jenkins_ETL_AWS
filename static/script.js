const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('search-input');
const checkboxes = document.querySelectorAll('.checkboxes input[type="checkbox"]');
const paginationInput = document.getElementById('pagination');
const searchResults = document.getElementById('search-results');

searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const keyword = searchInput.value.trim();
    const filters = [];
    checkboxes.forEach((checkbox) => {
        if (checkbox.checked) {
            filters.push(checkbox.name);
        }
    });
    const pagination = paginationInput.value;
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            keyword,
            filters,
            pagination,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            const tableHtml = data.tableHtml;
            searchResults.innerHTML = tableHtml;
        });
});
