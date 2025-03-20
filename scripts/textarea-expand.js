window.addEventListener('load', () => {
    var textareas = document.querySelectorAll("textarea");
    textareas.forEach(textarea => {
        textarea.style.height = textarea.scrollHeight + "px";

        textarea.addEventListener("input", function () {
            this.style.height = "";
            this.style.height = this.scrollHeight + "px";
        })
    });
});
