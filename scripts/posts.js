window.addEventListener('load', () => {
    document.querySelectorAll(".post-content").forEach(el => {
        // For whatever reason, all posts were appended with a newline and some spaces,
        // This removes that
        el.innerText = el.textContent.split(`
        `)[1];
    });
})