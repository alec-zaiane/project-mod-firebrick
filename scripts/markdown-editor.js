import { marked } from "marked"; // Import the markdown converter
import DOMPurify from "dompurify";

window.addEventListener('load', () => {
    let content = document.querySelector("[name='content']");
    let type_selector = document.querySelector("[name='post_type']");
    // Initialization for edit posts
    apply_preview();
    // On change of text
    content.addEventListener("input", () => {
        apply_preview();
    });
    // On change of selector, for changing between markdown and not
    type_selector.addEventListener("change", () => {
        apply_preview();
    });
})

function apply_preview() {
    let preview = document.getElementById("preview");
    let type_selector = document.querySelector("[name='post_type']");
    let content = document.querySelector("[name='content']");
    preview.innerText = content.value;
    if (type_selector.value == "MD") {
        preview.innerHTML = DOMPurify.sanitize(marked(preview.innerText));
    }
}