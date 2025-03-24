import { marked } from "marked"; // Import the markdown converter
import DOMPurify from "dompurify";

window.addEventListener('load', () => {
    let content = document.querySelector("[name='content']");
    let type_selector = document.querySelector("[name='post_type']");
    let image_selector = document.getElementById("id_image");
    view_or_hide_content();
    view_or_hide_visibility();
    // Eventually, video_field
    // Initialization for edit posts
    apply_preview();
    apply_image_preview();
    apply_title_preview();
    apply_description_preview();
    // On change of text
    content.addEventListener("input", () => {
        apply_preview();
    });
    // On change of selector, for changing between markdown and not
    type_selector.addEventListener("change", () => {
        view_or_hide_content();
        apply_preview();
        apply_image_preview();
    });

    image_selector.addEventListener("change", () => {
        apply_image_preview();
    });

    let title = document.querySelector("[name='title']");
    title.addEventListener("input", () => {
        apply_title_preview();
    });

    let description = document.querySelector("[name='description']");
    description.addEventListener("input", () => {
        apply_description_preview();
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
            img.classList.add("post-image")
            img.id = "preview-image";
            preview.appendChild(img);
            if (image.files[0]) {
                img.src = URL.createObjectURL(image.files[0]);
            }
        }

    }
}

function apply_title_preview() {
    let title = document.querySelector("[name='title']");
    let title_preview = document.getElementById("preview-title");
    title_preview.innerText = title.value;
}

function apply_description_preview() {
    let description = document.querySelector("[name='description']");
    let description_preview = document.getElementById("preview-description");
    description_preview.innerText = description.value;
}

function apply_image_preview() {
    let img_preview = document.getElementById("preview-image");
    let image_selector = document.getElementById("id_image");
    let image_link = document.getElementById("image-field").querySelector("a");
    if (img_preview) {
        if (image_selector.files[0]) {
            img_preview.src = URL.createObjectURL(image_selector.files[0]);
        } else if (image_link?.href) {
            img_preview.src = image_link.href;
        }
    }
}

function view_or_hide_content() {
    let content_field = document.getElementById("content-field");
    let image_field = document.getElementById("image-field");
    let type_selector = document.querySelector("[name='post_type']");
    if (type_selector.value == "PT" || type_selector.value == "MD") {
        content_field.classList.toggle("invisible", false);
        content_field.querySelector("#id_content").required = true;
        image_field.classList.toggle("invisible", true);
        image_field.querySelector("#id_image").required = false;
        // video
    } else {
        content_field.classList.toggle("invisible", true);
        content_field.querySelector("#id_content").required = false;
        if (type_selector.value == "IMG") {
            image_field.classList.toggle("invisible", false);
            let current_image_link = image_field.querySelector("a");
            image_field.querySelector("#id_image").required = !current_image_link;
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
