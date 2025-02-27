// Usage:
/*
    <div name="generic-form-div">
        <form action="TARGET URL HERE">
            <input type="hidden" name="_method" value="METHOD HERE">
            <input OTHER INPUTS>
            <button type="submit">Submit</button>
        </form>
        <p name="success-response"></p>
        <p name="error-response"></p>
    </div>
*/
// Remember to use names instead of IDs so that multiple forms can be on the same page :)
// the form will send the request using the method specified in the hidden input _method
// and then display the `detail` field in success-response, and `error` field in error-response

// Additionally, values with names containing double underscores will be converted to nested objects
// eg: `name="user__username"` will be converted to `{user: {username: value}}`


function nestify_formData(formData) {
    // Converts a FormData object into a nested object based on `__` delimiters
    let outputFormData = new FormData();
    for (const pair of formData.entries()) {
        let [key, value] = pair;
        let key_chain = key.split("__");
        let current_obj = outputFormData;
        // traverse the key chain, creating objects if they don't exist
        for (let i = 0; i < key_chain.length - 1; i++) {
            if (!current_obj.has(key_chain[i])) {
                current_obj.append(key_chain[i], new FormData());
            }
            current_obj = current_obj.get(key_chain[i]);
        }
        // append the value to the last object in the chain
        current_obj.append(key_chain[key_chain.length - 1], value);
    }
    return outputFormData;
}

document.addEventListener("load", () => {
    var formDivs = document.getElementsByName("generic-form-div");
    formDivs.forEach((formDiv) => {
        let form = formDiv.querySelector("form");
        let successResponse = formDiv.querySelector("p[name='success-response']");
        let errorResponse = formDiv.querySelector("p[name='error-response']");

        form.addEventListener("submit", (event) => {
            event.preventDefault();
            let formData = new FormData(form);
            let method = formData.get("_method");
            formData = nestify_formData(formData);
            formData.delete("_method");
            if (!method) {
                console.error("No method specified for generic form, no action taken");
                return;
            }
            fetch(form.action, {
                method: method,
                body: formData,
            }).then((response) => {
                response.json().then((json) => {
                    successResponse.innerText = json.detail || "";
                    if (json.error) {
                        errorResponse.innerText = json;
                    }
                })
            });
        });
    });
});
