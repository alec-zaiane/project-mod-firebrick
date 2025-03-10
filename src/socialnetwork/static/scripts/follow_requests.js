document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/follow/requests/")
        .then(response => response.json())
        .then(data => {
            let count = data.length;
            let countElement = document.getElementById("follow-request-count");
            if (count > 0) {
                countElement.innerText = `(${count})`;
            } else {
                countElement.innerText = "";
            }
        })
        .catch(error => console.error("Error fetching follow request count:", error));
});
