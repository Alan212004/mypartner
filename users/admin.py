from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile, DeletedProfile, ProfileImage, Interest

class ProfileImageInline(admin.TabularInline):
    model = ProfileImage
    extra = 1  # Number of empty forms to display
    fields = ['image', 'caption']  # Customize fields to display
    readonly_fields = ['image']  # Prevent editing

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'is_verified', 'needs_verification' , 'gender', 'age', 'phone_number']
    list_filter = ['is_verified', 'gender']
    search_fields = ['user__username', 'first_name', 'last_name', 'email']
    inlines = [ProfileImageInline]

admin.site.register(Profile, ProfileAdmin)

class UserAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        DeletedProfile.objects.create(user=obj)  # Create DeletedProfile before deletion
        super().delete_model(request, obj)  # Call the original delete method

admin.site.unregister(User)  # Unregister default User admin
admin.site.register(User, UserAdmin)

class DeletedProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'deleted_at')  # Display necessary fields
    readonly_fields = ('user', 'deleted_at')
    search_fields = ['user__username']  # Search functionality for deleted profiles

admin.site.register(DeletedProfile, DeletedProfileAdmin)


def mark_as_accepted(modeladmin, request, queryset):
    queryset.update(status='accepted')
mark_as_accepted.short_description = "Mark selected interests as accepted"

class InterestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status')
    list_filter = ('status',)
    actions = [mark_as_accepted]

admin.site.register(Interest, InterestAdmin)

# # # # # # # # # # # # # # # # # # #

admin.site.site_header = "Matrimony Admin Page"
admin.site.site_title = "Matrimony Admin Portal"
admin.site.index_title = "Welcome to Matrimony Admin"