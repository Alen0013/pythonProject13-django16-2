from django.contrib import admin
from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'age', 'owner', 'created_at')
    list_filter = ('species', 'owner')
    search_fields = ('name', 'description')
