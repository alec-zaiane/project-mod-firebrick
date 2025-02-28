"use strict";
// Basic Usage:
/*
    <form name="generic-form" action="TARGET URL HERE">
        <input type="hidden" name="_method" value="METHOD HERE">
        (optional) <input type="hiden" name="_after_action" value="SEE BELOW FOR THIS ONE">

        <input OTHER INPUTS>
        <button type="submit">Submit</button>
        <div name="response-detail"></div>
        <div name="errorresponse-error"></div>
    </form>
*/
// Effects:
/* The script will parse the form data with the following rules:
    - any input with a name containing `__` will be converted to a nested object
    - the hidden input with the name `_method` will be used to determine the request method, and not included in the request
    - the returned JSON will be parsed, returned information will be displayed in `response-<xyz>` or `errorresponse-<xyz>` divs if they exist
        - normally you want to use `response-detail` for the main response
        - `errorresponse-xyz` will only be populated if the response is not successful
        - this follows the `__` rule, ie: `response-user__username` will display the response_json['user']['username']
*/

// Customization:
/* stuff can be in any order, so long as the parent/child relationships are intact
   However, any `response` or `errorresponse` divs will be emptied during each form submission, so they should be empty normally
*/

// the _after input:
/* is a space separated list of actions to take after the user clicks submit
    - confirm: will show a confirm dialog before submitting the form
    - reload: will reload the page after the form is submitted
*/


function nestify_formData(formData) {
    // Converts a FormData object into a nested object based on `__` delimiters
    // eg: {"user__username": "test"} -> {user: {username : "test"}}
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

function flatten_object(responseData) {
    // take in a nested object and return a flat list of key-value pairs (the opposite of nestify_formData)
    // eg: {user: {username: "test"}} -> {"user__username": "test"}
    // *** all values are arrays, even if they are single values *** (makes it easier to display in the response divs)

    let outputData = new Object();
    for (const pair of Object.entries(responseData)) {
        let [key, value] = pair;
        if (value instanceof Object && !(value instanceof Array)) {
            let nestedData = flatten_object(value);
            for (const nestedPair of Object.entries(nestedData)) {
                let [nestedKey, nestedValue] = nestedPair;
                outputData[key + "__" + nestedKey] = nestedValue;
            }
        } else {
            if (value instanceof Array) {
                outputData[key] = value;
            } else {
                outputData[key] = [value];
            }
        }
    }
    return outputData;

}

function process_response(response, formElement) {
    // process the response from the server, displaying the response in the appropriate divs
    let normalResponses = formElement.querySelectorAll("div[name^='response-']");
    let errorResponses = formElement.querySelectorAll("div[name^='errorresponse-']");
    // wipe the response divs
    normalResponses.forEach((element) => {
        element.innerHTML = "";
    });
    errorResponses.forEach((element) => {
        element.innerHTML = "";
    });
    // now populate the response divs
    response.json().then((data) => {
        let flattenedData = flatten_object(data);
        // normal responses
        normalResponses.forEach((element) => {
            let key = element.getAttribute("name").slice(9);
            if (key in flattenedData) {
                flattenedData[key].forEach((value) => {
                    let displayElement = document.createElement("p");
                    displayElement.innerText = value;
                    element.appendChild(displayElement);
                });
            }
        });
        // stop if the response is successful
        if (response.ok) {
            return;
        }
        // error responses
        errorResponses.forEach((element) => {
            let key = element.getAttribute("name").slice(14);
            if (key in flattenedData) {
                flattenedData[key].forEach((value) => {
                    let displayElement = document.createElement("p");
                    displayElement.innerText = value;
                    element.appendChild(displayElement);
                });
            }
        });
    });

}

document.addEventListener("DOMContentLoaded", () => {
    var forms = document.querySelectorAll("form[name='generic-form']");
    // console.log(forms.length);
    forms.forEach((form) => {
        let successResponse = form.querySelector("p[name='success-response']");
        let errorResponse = form.querySelector("p[name='error-response']");

        form.addEventListener("submit", (event) => {
            event.preventDefault();
            let formData = new FormData(form);
            let method = formData.get("_method");
            let afterActions = formData.get("_after_action").split(" ");
            formData.delete("_method");
            formData.delete("_after_action");
            formData = nestify_formData(formData);
            if (!method) {
                console.error("No method specified for generic form, no action taken");
                return;
            }
            if (afterActions.includes("confirm")) {
                if (!confirm("Are you sure you want to submit this?")) {
                    return;
                }
            }
            fetch(form.action, {
                method: method,
                body: formData,
                headers: {
                    'X-CSRFToken': document.getElementsByName("csrfmiddlewaretoken")[0].value,
                    'Accept': 'application/json',
                }
            }).then((response) => {
                process_response(response, form);
            }).then(() => {
                if ("reload" in afterActions) {
                    location.reload();
                }
            });
        });
    });
});
