from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Page

class PageAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'url')

admin.site.register(Category)
admin.site.register(Page, PageAdmin)
