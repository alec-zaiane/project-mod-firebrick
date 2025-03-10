window.addEventListener('load', () => {
    document.querySelectorAll(".post-content").forEach(el => {
        // For whatever reason, all posts were appended with a newline and some spaces,
        // This removes that
        el.innerText = el.textContent.split(`
        `)[1];
    });

    document.querySelectorAll(".likes-box").forEach(el => {
        let viewer = JSON.parse(el.querySelector('#viewer').textContent);
        let like_authors = JSON.parse(el.querySelector('#like_authors').textContent);
        if (like_authors.includes(viewer)) {
            // Eventually, unliking should exist
            el.querySelector(".like-button").disabled = true;
        }
    })

    var comment_textarea = document.querySelector(".add-comment-text");
    if (comment_textarea) {
        comment_textarea.style.height = comment_textarea.scrollHeight + "px";

        comment_textarea.addEventListener("input", function() {
            this.style.height = "auto";
            this.style.height = this.scrollHeight + "px";
        });
    }
    document.querySelectorAll(".settings").forEach(el => {
        el.querySelector(".settings-dropdown-content").style.visibility = "hidden"; // Initialization
        el.querySelector(".settings-dropdown").addEventListener("click", () => {
            var visibility = el.querySelector(".settings-dropdown-content").style.visibility;
            var new_visibility = visibility == "hidden" ? "visible" : "hidden";
            document.querySelectorAll(".settings-dropdown-content").forEach(el => {
                el.style.visibility = "hidden";
            });

            el.querySelector(".settings-dropdown-content").style.visibility = new_visibility;
        });
    })

    window.addEventListener("click", (event) => {
        if (!event.target.matches(".settings-dropdown")) {
            document.querySelectorAll(".settings-dropdown-content").forEach(el => {
                el.style.visibility = "hidden";
            });
        }
    })
})
