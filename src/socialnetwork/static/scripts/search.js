document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("search-form").addEventListener("submit", function (event) {
        event.preventDefault();
        let query = document.getElementById("search-input").value;
        fetch(`/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                let resultsContainer = document.getElementById("search-results");
                resultsContainer.innerHTML = "";
                if (data.authors.length === 0) {
                    resultsContainer.innerHTML = "<p>No users found.</p>";
                    return;
                }
                data.authors.forEach(author => {
                    let userElement = document.createElement("div");
                    userElement.innerHTML = `<a href="/author/${author.uuid}">${author.display_name} (@${author.username})</a>`;
                    resultsContainer.appendChild(userElement);
                });
            })
            .catch(error => console.error("Error fetching search results:", error));
    });
});


