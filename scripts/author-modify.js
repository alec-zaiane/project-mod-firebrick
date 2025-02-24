document.addEventListener("DOMContentLoaded", function() {
    forms = document.getElementsByName("modify-author-form");
    forms.forEach(function(form) {
        responseDiv = form.querySelector("[name=server-response]");
        form.addEventListener("submit", function(event) {
            event.preventDefault();
            let formData = new FormData(form);
            let url = form.action;
            let method = formData.get("_method");
            formData.delete("_method");
            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-CSRFToken': document.getElementsByName("csrfmiddlewaretoken")[0].value,
                    'Accept': 'application/json',
                }
            }).then(response => {
                if (response.ok) {
                    response.json().then(data => {
                        console.log(response);
                        responseDiv.innerHTML = "Success!";
                    });
                } else {
                    response.json().then(data => {
                        console.log(response);
                        responseDiv.innerHTML = "Error: " + data.error;
                    });
                }
            });
        });
    });
});