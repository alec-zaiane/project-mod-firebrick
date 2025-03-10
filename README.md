# Team
- Alec Zaiane
- Mosa Yaqoobi
- Tanveer Multani
- Reuben John
- ravyn Hardcastle
- Imaad Khan

> [!NOTE]
> Commit/Branch Types
> - `feat`: A new feature
> - `fix`: A bug fix
> - `docs`: Documentation changes (e.g., `README`, inline comments)
> - `refactor`: Code changes that neither fix a bug nor add a feature
> - `perf`: Performance improvements
> - `test`: Adding or updating tests
> - `ci`: Changes to CI/CD configuration files and scripts (github actions)
> - `chore`: Maintenance tasks, like dependency upgrades or cleanup



##GPT/Copilot Documentation:
1. Copilot auto-complete was used in VS

GPT PROMPT: This is my post_submission_card.html, why is it that when I post an image I'm getting an error showing it's giving a GET req. Linked my html file, along with the error given with the request. 

Response: Keep method="post" But Prevent Default in JS
If you must keep method="post" for some reason, ensure your JavaScript code prevents the default submission. For example:

html
Copy
Edit
<script>
document.querySelector("form[name='generic-form']").addEventListener("submit", function(e) {
    e.preventDefault();  // stops the normal POST
    // Then do your AJAX request or let generic-form.min.js do it
});
</script>
- This ended up not working it was forcing "post" when we had a method to leave it working so I swapped it back.

GPT PROMPT: When I click the image to use, then I click create image post button and that button redirects me to the django framework as you saw above where I am able to see the markdown. So how would the user see this markdown, so that they can copy it and use it later?

Response: 
✅ Update post_card.html
Modify your post_card.html so that if a post contains an image, it will display its corresponding Markdown link right below it.

html
Copy
Edit
<article class="post-card">
    <header>
        <h3>{{ post.author.username }}</h3>
        <span class="post-meta">
            Posted: {{ post.date_created|date:"F j, Y, g:i a" }}
            {% if post.date_edited %}
            (Edited: {{ post.date_edited|date:"F j, Y, g:i a" }})
            {% endif %}
        </span>
    </header>

    <div class="post-content {{ post.css_class }}">
        {% if post.image %}
            <img src="{{ post.image.url }}" alt="Image Post" class="post-image">
            
            <!-- Display Markdown Link Below Image -->
            <div class="markdown-container">
                <p><strong>Markdown for this image:</strong></p>
                <textarea class="markdown-box" readonly>[![{{ post.image.url|cut:"/media/hosted_images/" }}]({{ post.image.url }})]</textarea>
            </div>
        {% else %}
            {{ post.content }}
        {% endif %}
    </div>

    <footer>
        <span class="visibility">{{ post.get_visibility_type_display }}</span>
        {% if post.author == viewer %}
            <a href="{% url 'socialnetwork:edit_post' post.uuid %}" class="edit-button">Edit</a>
        {% endif %}
    </footer>
</article>
🎯 How This Works
✅ Automatically adds a Markdown URL to every image post
✅ Users can copy and paste the Markdown anywhere

GPT PROMPT: Gave it an image of my profile page and the error I was seeing. My image posts are now being shown like this and when I make a new post it's not going to the stream page.

Response: 1️⃣ Check if JavaScript is Handling Markdown

Open the browser console (F12 → Console tab)
Run this command:
js
Copy
Edit
document.querySelectorAll('.post-content').forEach(e => console.log(e.innerHTML))
If you see raw markdown (![image](url) instead of an <img> tag), then the markdown-renderer.js is not working.
2️⃣ Verify If Images Are in the Response JSON

In the Network tab (F12 → Network → Reload page)
Check the API response for GET /stream
See if the JSON contains image URLs inside the post data.
3️⃣ Manually Add an Image in Your Template

Edit post_card.html to force an image to show:
html
Copy
Edit
<div class="post-content {{ post.css_class }}">
    {% if post.image %}
        <img src="{{ post.image.url }}" alt="Image Post" class="post-image">
    {% endif %}
    {{ post.content|safe }}
</div>
This forces images to display. If they appear, then the markdown-rendering is the issue.
Issue 2: New Posts Aren't Redirecting to Stream
If new posts aren't redirecting properly, the problem is likely in create_post.html or the API response handling.

✅ Debugging Steps
1️⃣ Check the API Response When Posting an Image

Open Developer Tools (F12) → Network Tab
Click "Create Image Post"
Look for the POST /api/v1/create_image_post request
Does it return a success response (201 Created)?
Does it contain the "markdown" key in the response?
2️⃣ Fix the Form Handling in create_post.html

Add this after the <form> to check if the request is firing:
html
Copy
Edit
<script>
    document.getElementById("image-upload-form").addEventListener("submit", function(event) {
        event.preventDefault();
        let formData = new FormData(this);

        fetch(this.action, {
            method: "POST",
            body: formData,
            headers: {
                'X-CSRFToken': document.getElementsByName("csrfmiddlewaretoken")[0].value
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log("Response received:", data);  // Debugging step
            if (data.markdown) {
                document.getElementById("markdown-container").style.display = "block";
                document.getElementById("markdown-output").value = data.markdown;
            }
            window.location.href = "/stream"; // Redirect to the stream page
        })
        .catch(error => console.error("Error:", error));
    });
</script>
🔹 This will:
Log the response to check if it's correct.
Redirect the user to /stream if the post is created successfully.
3️⃣ Check Django Views (views_api.py) Make sure the API is returning the correct response, including:

python
Copy
Edit
return Response({
    "detail": "Image post created",
    "post": serializer.data,
    "markdown": f"![{post.image.url.split('/')[-1]}]({post.image.url})"
}, status=201)
This ensures that the response contains Markdown for the uploaded image.






