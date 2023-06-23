from django.contrib import admin

from .models import FlatsUser


@admin.register(FlatsUser)
class AdvUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name',
                    'last_name', 'email', 'is_email_activated']  # поля для отображения
    search_fields = ['username']   # поиск по этим полям
