document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("search-form");
    const searchInput = document.getElementById("search-input");
    const resultsContainer = document.getElementById("search-results");

    if (!searchForm || !searchInput || !resultsContainer) return;

    searchForm.addEventListener("submit", function (event) {
        event.preventDefault();
        let query = searchInput.value.trim();
        let viewer_url = searchForm.elements['viewer_host_url'].value;

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
                    const uuid = author.uuid;

                    // HTML creates this:
                    /* <div class="search-result">
                        <img src="<IMG>" class="profile-image">
                        <div class="search-name-and-link">
                            <a href="/authors/<UUID>/" class="names">
                                <h3 class="display-name"><NAME></h3>
                            </a>
                            <a id="external-node-select-http://<URL>/api" class="external-node-select" href="http://<URL>">
                                <h6 class="external-tag" title="From External Node">@<URL></h6>
                            </a>
                        </div>
                    </div> */
                    if (uuid) {
                        const names = document.createElement("div");
                        names.classList.add("search-result");
                        if (author.profileImage) {
                            const img = document.createElement("img");
                            img.src = author.profileImage;
                            img.classList.add("profile-image");
                            names.appendChild(img);
                        }
                        const name_and_link = document.createElement("div");
                        name_and_link.classList.add("search-name-and-link");
                        names.appendChild(name_and_link);
                        const link = document.createElement("a");
                        link.href = `/authors/${uuid}/`;
                        link.classList.add("names");
                        const displayName = document.createElement("h3");
                        displayName.classList.add("display-name");
                        displayName.textContent = author.displayName;
                        link.appendChild(displayName);
                        name_and_link.appendChild(link);
                        if (author.host_url && author.host_url != viewer_url) {
                            const host = document.createElement("a");
                            host.id = "external-node-select-" + author.host_url;
                            host.classList.add("external-node-select");
                            host.href = author.host_url.replace("/api", "");
                            const hostTag = document.createElement("h6");
                            hostTag.classList.add("external-tag");
                            hostTag.title = "From External Node";
                            hostTag.textContent = "@" + author.host_url.replace("https://", "").replace("http://", "").replace("/api", "");
                            host.appendChild(hostTag);
                            name_and_link.appendChild(host);
                        }

                        resultsContainer.appendChild(names);
                    }
                });
            })
            .catch(error => {
                console.error("Error fetching search results:", error);
                resultsContainer.innerHTML = "<p>Error fetching results.</p>";
            });
    });
});
