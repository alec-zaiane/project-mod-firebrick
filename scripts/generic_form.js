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
