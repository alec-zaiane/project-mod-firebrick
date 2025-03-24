document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("search-form");
    const searchInput = document.getElementById("search-input");
    const resultsContainer = document.getElementById("search-results");

    if (!searchForm || !searchInput || !resultsContainer) return;

    searchForm.addEventListener("submit", function (event) {
        event.preventDefault();
        let query = searchInput.value.trim();

        if (query === "") {
            resultsContainer.innerHTML = "<p>Please enter a search term.</p>";
            return;
        }

        fetch(`/api/authors/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                resultsContainer.innerHTML = "";
                if (data.length === 0) {
                    resultsContainer.innerHTML = "<p>No users found.</p>";
                    return;
                }

                data.forEach(author => {
                    const uuidMatch = author.id.match(/authors\/([a-f0-9\-]+)/i);
                    const uuid = uuidMatch ? uuidMatch[1] : null;

                    if (uuid) {
                        const link = document.createElement("a");
                        link.href = `/authors/${uuid}/`;
                        link.classList.add("names");
                        if (author.profileImage) {
                            const img = document.createElement("img");
                            img.src = author.profileImage;
                            img.classList.add("profile-image");
                            link.appendChild(img);
                        }
                        const displayName = document.createElement("h3");
                        displayName.classList.add("display-name");
                        displayName.textContent = author.displayName;
                        link.appendChild(displayName);
                        resultsContainer.appendChild(link);
                    }
                });
            })
            .catch(error => {
                console.error("Error fetching search results:", error);
                resultsContainer.innerHTML = "<p>Error fetching results.</p>";
            });
    });
});
