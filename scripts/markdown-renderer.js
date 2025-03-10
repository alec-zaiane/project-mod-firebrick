import { marked } from "marked"; // Import the markdown converter
import DOMPurify from "dompurify";

window.addEventListener('load', () => {
    document.querySelectorAll(".post-content.post-markdown").forEach(el => {
        el.innerHTML = DOMPurify.sanitize(marked(el.innerText));
    });
})
