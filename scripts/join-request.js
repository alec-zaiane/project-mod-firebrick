document.addEventListener("DOMContentLoaded", function() {
    forms = document.getElementsByName("join-request-form");
    forms.forEach(function(form) {
        genericResponseDiv = document.getElementById("generic_response");
        usernameResponseDiv = document.getElementById("username_response");
        passwordResponseDiv = document.getElementById("password_response");
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
                        genericResponseDiv.innerHTML = data.detail;
                    });
                } else {
                    response.json().then(data => {
                        if (data.username) {
                            usernameResponseDiv.innerHTML = "Error: " + data.username;
                        }
                        if (data.password) {
                            passwordResponseDiv.innerHTML = "Error: " + data.password;
                        }
                        if (data.error) {
                            genericResponseDiv.innerHTML = "Error: " + data.error;
                        }
                    });
                }
            });
        });
    });
});