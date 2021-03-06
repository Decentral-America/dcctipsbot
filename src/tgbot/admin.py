from django.contrib import admin
from tgbot.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'user_id', 'username', 'first_name', 'last_name', 
        'language_code', 'created_at', 'updated_at', 
    ]
    search_fields = ('username', 'first_name', 'last_name')