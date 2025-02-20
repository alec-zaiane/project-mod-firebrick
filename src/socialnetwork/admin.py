from django.contrib import admin
from . import models

@admin.register(models.LocalAuthor)
class LocalAuthorAdmin(admin.ModelAdmin):
    """
    Admin configuration for LocalAuthor model.
    
    Attributes:
        list_display (list): Fields to display in the admin list view
        filter_horizontal (list): Fields to display with horizontal filter interface
    """
    list_display = ['user', 'get_id']
    filter_horizontal = ['following']
    
    def get_id(self, obj):
        """
        Get the UUID of the author for display in admin list.
        
        Args:
            obj (LocalAuthor): The LocalAuthor instance
            
        Returns:
            str: The string representation of the author's UUID
        """
        return str(obj.uuid)
    get_id.short_description = 'ID' 

    def get_form(self, request, obj=None, **kwargs):
        """
        Customize the admin form for LocalAuthor.
        
        Args:
            request (HttpRequest): The current request
            obj (LocalAuthor, optional): The LocalAuthor being edited, or None for creation
            **kwargs: Additional keyword arguments
            
        Returns:
            ModelForm: The customized form for the admin interface
        """
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['user'].help_text = 'Select the user account for this author'
        return form


admin.site.register(models.PostTextBased)
