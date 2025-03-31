document.addEventListener('DOMContentLoaded', () => {
    const followForm = document.getElementById('follow-form');
    if (!followForm) return;

    followForm.removeAttribute('name');

    followForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        const data = {
            type: 'follow',
            summary: formData.get('summary'),
            actor: {
                type: formData.get('actor__type'),
                id: formData.get('actor__id'), 
                host: formData.get('actor__host'),
                displayName: formData.get('actor__displayName'),
                profileImage: formData.get('actor__profileImage'),
                page: formData.get('actor__page')
            },
            object: {
                type: formData.get('object__type'),
                id: formData.get('object__id'), // Don't decode here, send as-is
                host: formData.get('object__host'),
                displayName: formData.get('object__displayName'),
                page: formData.get('object__page'),
                profileImage: formData.get('object__profileImage')
            }
        };

        console.log('Sending follow request:', data);

        try {
            const response = await fetch(e.target.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                body: JSON.stringify(data)
            });

            console.log('Response status:', response.status);
            const responseData = await response.json();
            console.log('Response data:', responseData);

            if (response.ok) {
                window.location.reload();
            } else {
                const errorDiv = e.target.querySelector('[name="errorresponse-error"]');
                if (errorDiv) {
                    errorDiv.textContent = responseData.error || 'Failed to send follow request';
                }
            }
        } catch (err) {
            console.error('Error sending follow request:', err);
            const errorDiv = e.target.querySelector('[name="errorresponse-error"]');
            if (errorDiv) {
                errorDiv.textContent = 'Network error occurred';
            }
        }
    });
});
