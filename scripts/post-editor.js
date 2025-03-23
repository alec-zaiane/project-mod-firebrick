import { marked } from "marked"; // Import the markdown converter
import DOMPurify from "dompurify";

window.addEventListener('load', () => {
    let content = document.querySelector("[name='content']");
    let type_selector = document.querySelector("[name='post_type']");
    view_or_hide_content();
    view_or_hide_visibility();
    // Eventually, video_field
    // Initialization for edit posts
    apply_preview();
    // On change of text
    content.addEventListener("input", () => {
        apply_preview();
    });
    // On change of selector, for changing between markdown and not
    type_selector.addEventListener("change", () => {
        view_or_hide_content();
        apply_preview();
    });

    let title = document.querySelector("[name='title']");
    title.addEventListener("input", () => {
        let title_preview = document.getElementById("preview-title");
        title_preview.innerText = title.value;
    });

    let description = document.querySelector("[name='description']");
    description.addEventListener("input", () => {
        let description_preview = document.getElementById("preview-description");
        description_preview.innerText = description.value;
    });

    let visibility_selector = document.querySelector("[name='visibility_type']");
    visibility_selector.addEventListener("change", () => {
        view_or_hide_visibility();
    });
})

function apply_preview() {
    let preview = document.getElementById("preview");
    let type_selector = document.querySelector("[name='post_type']");
    let content = document.querySelector("[name='content']");
    let image = document.querySelector("[name='image']");
    if (type_selector.value == "PT" || type_selector.value == "MD") {
        preview.innerText = content.value;
        if (type_selector.value == "MD") {
            preview.innerHTML = DOMPurify.sanitize(marked(preview.innerText));
        }
    } else {
        preview.innerHTML = "";
        if (type_selector.value == "IMG") {
            let img = document.createElement("img");
            img.classList.add("preview-image")
            img.id = "preview-image";
            preview.appendChild(img);
            if (image.files[0]) {
                img.src = URL.createObjectURL(image.files[0]);
            }

        }

    }

}

function view_or_hide_content() {
    let content_field = document.querySelector("#content-field");
    let image_field = document.querySelector("#image-field");
    let type_selector = document.querySelector("[name='post_type']");
    if (type_selector.value == "PT" || type_selector.value == "MD") {
        content_field.style.display = "flex";
        image_field.style.display = "none";
        // video
    } else {
        content_field.style.display = "none";
        if (type_selector.value == "IMG") {
            image_field.style.display = "flex";
        }
        // video
    }
}

function view_or_hide_visibility() {
    let visibility_selector = document.querySelector("[name='visibility_type']");
    let visibility = visibility_selector.value;
    let public_visibility = document.getElementById("public-visibility");
    let unlisted_visibility = document.getElementById("unlisted-visibility");
    let friends_visibility = document.getElementById("friends-only-visibility");
    switch (visibility) {
        case "PB":
            public_visibility.style.display = "block";
            unlisted_visibility.style.display = "none";
            friends_visibility.style.display = "none";
            break;
        case "UL":
            public_visibility.style.display = "none";
            unlisted_visibility.style.display = "block";
            friends_visibility.style.display = "none";
            break;
        case "FO":
            public_visibility.style.display = "none";
            unlisted_visibility.style.display = "none";
            friends_visibility.style.display = "block";
            break;
    }
}
