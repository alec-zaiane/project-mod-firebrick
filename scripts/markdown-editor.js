import { marked } from "marked"; // Import the markdown converter
import DOMPurify from "dompurify";

window.addEventListener('load', () => {
    let content = document.querySelector("[name='content']");
    let type_selector = document.querySelector("[name='post_type']");
    let preview = document.getElementById("preview");
    content.addEventListener("input", () => {
        preview.innerText = content.value;
        if (type_selector.value == "MD") {
            preview.innerHTML = DOMPurify.sanitize(marked(preview.innerText));
        }
    });
})