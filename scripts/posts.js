window.addEventListener('load', () => {
    document.querySelectorAll(".post-content .text").forEach(el => {
        // For whatever reason, all posts were appended with a newline and some spaces,
        // This removes that
        el.innerText = el.textContent.split(`
        `)[1];
    });

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
